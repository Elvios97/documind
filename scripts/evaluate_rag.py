import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from services.rag_quality_service import aggregate_quality_results, evaluate_retrieval_sources  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Bewertet Documind-Retrieval anhand lokaler Testfaelle.")
    parser.add_argument("cases", type=Path, help="JSON-Datei mit Retrieval-Testfaellen")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    results = []
    for case in cases:
        response = _post_json(
            f"{args.base_url.rstrip('/')}/rag/retrieve",
            {
                "document_ids": case["document_ids"],
                "question": case["question"],
                "top_k": case.get("top_k", 8),
            },
        )
        result = evaluate_retrieval_sources(
            name=case["name"],
            expected_document_ids=case.get("expected_document_ids", []),
            expected_pages=case.get("expected_pages", {}),
            sources=response.get("sources", []),
        )
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(
            f"[{status}] {result.name}: coverage={result.document_coverage:.2f}, "
            f"rr={result.reciprocal_rank:.2f}, pages={result.page_requirements_passed}"
        )

    summary = aggregate_quality_results(results)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["passed_count"] == summary["case_count"] else 1


def _post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Retrieval-API antwortet mit HTTP {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"Retrieval-API ist nicht erreichbar: {error.reason}") from error


if __name__ == "__main__":
    raise SystemExit(main())
