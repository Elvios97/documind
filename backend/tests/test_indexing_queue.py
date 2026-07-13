import asyncio

from services.indexing_queue import IndexingQueue


def test_indexing_queue_processes_jobs_serially_and_deduplicates() -> None:
    asyncio.run(asyncio.wait_for(_run_queue_test(), timeout=2))


async def _run_queue_test() -> None:
    queue = IndexingQueue()
    processed: list[str] = []
    release_first = asyncio.Event()
    first_started = asyncio.Event()

    async def processor(document_id: str) -> None:
        processed.append(document_id)
        if document_id == "doc-1":
            first_started.set()
            await release_first.wait()

    queue.start(processor)
    assert queue.enqueue("doc-1") is True
    assert queue.enqueue("doc-1") is False
    assert queue.enqueue("doc-2") is True
    await asyncio.wait_for(first_started.wait(), timeout=1)
    assert processed == ["doc-1"]
    assert queue.is_active("doc-1") is True
    assert queue.get_position("doc-1") == 0
    assert queue.get_position("doc-2") == 1
    assert await queue.cancel("doc-2") is True
    assert queue.get_position("doc-2") is None
    release_first.set()
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    assert processed == ["doc-1"]
    await asyncio.wait_for(queue.stop(), timeout=1)


def test_indexing_queue_cancels_active_job_and_continues() -> None:
    asyncio.run(asyncio.wait_for(_run_active_cancel_test(), timeout=2))


async def _run_active_cancel_test() -> None:
    queue = IndexingQueue()
    processed: list[str] = []
    blocker = asyncio.Event()
    first_started = asyncio.Event()

    async def processor(document_id: str) -> None:
        processed.append(document_id)
        if document_id == "doc-1":
            first_started.set()
            await blocker.wait()

    queue.start(processor)
    queue.enqueue("doc-1")
    queue.enqueue("doc-2")
    await asyncio.wait_for(first_started.wait(), timeout=1)

    assert await asyncio.wait_for(queue.cancel("doc-1"), timeout=1) is True
    await asyncio.sleep(0)
    await asyncio.sleep(0)

    assert processed == ["doc-1", "doc-2"]
    await asyncio.wait_for(queue.stop(), timeout=1)
