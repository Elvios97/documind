import pytest

from services.rag_quality_service import aggregate_quality_results, evaluate_retrieval_sources


def test_evaluate_retrieval_sources_measures_coverage_rank_and_pages() -> None:
    result = evaluate_retrieval_sources(
        name="Vergleich",
        expected_document_ids=["doc-a", "doc-b"],
        expected_pages={"doc-a": [2], "doc-b": [4, 5]},
        sources=[
            {"document_id": "doc-a", "page_number": 2},
            {"document_id": "doc-b", "page_number": 5},
        ],
    )

    assert result.passed is True
    assert result.document_coverage == 1.0
    assert result.reciprocal_rank == 1.0
    assert result.page_requirements_passed is True


def test_aggregate_quality_results_reports_failures() -> None:
    passing = evaluate_retrieval_sources("Pass", ["doc-a"], {}, [{"document_id": "doc-a", "page_number": 1}])
    failing = evaluate_retrieval_sources("Fail", ["doc-b"], {}, [{"document_id": "doc-a", "page_number": 1}])

    summary = aggregate_quality_results([passing, failing])

    assert summary["case_count"] == 2
    assert summary["passed_count"] == 1
    assert summary["pass_rate"] == pytest.approx(0.5)
    assert summary["mean_coverage"] == pytest.approx(0.5)
