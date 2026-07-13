import asyncio
from collections.abc import Awaitable, Callable, Iterable


IndexProcessor = Callable[[str], Awaitable[None]]


class IndexingQueue:
    """Verarbeitet Indexierungsjobs seriell und verhindert doppelte Eintraege."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[str] | None = None
        self._pending_order: list[str] = []
        self._cancelled_pending: set[str] = set()
        self._queued_document_ids: set[str] = set()
        self._worker: asyncio.Task[None] | None = None
        self._processor: IndexProcessor | None = None
        self._active_document_id: str | None = None
        self._active_task: asyncio.Task[None] | None = None

    def start(self, processor: IndexProcessor, pending_document_ids: Iterable[str] = ()) -> None:
        if self._worker is not None and not self._worker.done():
            return
        self._queue = asyncio.Queue()
        self._pending_order.clear()
        self._cancelled_pending.clear()
        self._queued_document_ids.clear()
        self._processor = processor
        self._worker = asyncio.create_task(self._run())
        for document_id in pending_document_ids:
            self.enqueue(document_id)

    def enqueue(self, document_id: str) -> bool:
        if not document_id or document_id in self._queued_document_ids:
            return False
        if self._queue is None or self._worker is None or self._worker.done():
            raise RuntimeError("Die Indexierungsqueue wurde noch nicht gestartet.")
        self._queued_document_ids.add(document_id)
        self._pending_order.append(document_id)
        self._queue.put_nowait(document_id)
        return True

    async def cancel(self, document_id: str) -> bool:
        if document_id == self._active_document_id and self._active_task is not None:
            self._active_task.cancel()
            await asyncio.gather(self._active_task, return_exceptions=True)
            await asyncio.sleep(0)
            return True
        if document_id not in self._queued_document_ids:
            return False
        self._cancelled_pending.add(document_id)
        self._pending_order.remove(document_id)
        self._queued_document_ids.discard(document_id)
        return True

    def contains(self, document_id: str) -> bool:
        return document_id in self._queued_document_ids

    def is_active(self, document_id: str) -> bool:
        return document_id == self._active_document_id

    def get_position(self, document_id: str) -> int | None:
        if self.is_active(document_id):
            return 0
        try:
            return self._pending_order.index(document_id) + 1
        except ValueError:
            return None

    async def stop(self) -> None:
        worker = self._worker
        self._worker = None
        if worker is not None:
            worker.cancel()
            await asyncio.gather(worker, return_exceptions=True)
        self._queue = None
        self._pending_order.clear()
        self._cancelled_pending.clear()
        self._queued_document_ids.clear()
        self._processor = None
        self._active_document_id = None
        self._active_task = None

    async def _run(self) -> None:
        assert self._queue is not None
        assert self._processor is not None
        while True:
            document_id = await self._queue.get()
            if document_id in self._cancelled_pending:
                self._cancelled_pending.discard(document_id)
                self._queue.task_done()
                continue
            if document_id in self._pending_order:
                self._pending_order.remove(document_id)
            self._active_document_id = document_id
            self._active_task = asyncio.create_task(self._processor(document_id))
            try:
                await self._active_task
            except asyncio.CancelledError:
                current_task = asyncio.current_task()
                if current_task is not None and current_task.cancelling():
                    raise
            except Exception:
                # Ein einzelner Job darf nachfolgende Dokumente nicht blockieren.
                pass
            finally:
                self._queued_document_ids.discard(document_id)
                self._active_document_id = None
                self._active_task = None
                self._queue.task_done()


indexing_queue = IndexingQueue()
