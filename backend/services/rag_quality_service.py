from typing import Any

from pydantic import BaseModel, Field


class RetrievalQualityResult(BaseModel):
    name: str
    passed: bool
    document_coverage: float = Field(..., ge=0.0, le=1.0)
    reciprocal_rank: float = Field(..., ge=0.0, le=1.0)
    page_requirements_passed: bool
    missing_document_ids: list[str]


def evaluate_retrieval_sources(
    name: str,
    expected_document_ids: list[str],
    expected_pages: dict[str, list[int]],
    sources: list[dict[str, Any]],
) -> RetrievalQualityResult:
    """Bewertet Dokumentabdeckung, ersten relevanten Rang und optionale Seitentreffer."""
    expected_ids = list(dict.fromkeys(expected_document_ids))
    found_ids = {str(source.get("document_id", "")) for source in sources}
    missing_ids = [document_id for document_id in expected_ids if document_id not in found_ids]
    coverage = 1.0 if not expected_ids else (len(expected_ids) - len(missing_ids)) / len(expected_ids)

    first_relevant_rank = next(
        (
            index
            for index, source in enumerate(sources, start=1)
            if str(source.get("document_id", "")) in expected_ids
        ),
        None,
    )
    reciprocal_rank = 0.0 if first_relevant_rank is None else 1.0 / first_relevant_rank

    page_requirements_passed = all(
        any(
            str(source.get("document_id", "")) == document_id
            and int(source.get("page_number", 0)) in allowed_pages
            for source in sources
        )
        for document_id, allowed_pages in expected_pages.items()
        if allowed_pages
    )

    return RetrievalQualityResult(
        name=name,
        passed=not missing_ids and page_requirements_passed,
        document_coverage=coverage,
        reciprocal_rank=reciprocal_rank,
        page_requirements_passed=page_requirements_passed,
        missing_document_ids=missing_ids,
    )


def aggregate_quality_results(results: list[RetrievalQualityResult]) -> dict[str, float | int]:
    if not results:
        return {"case_count": 0, "passed_count": 0, "pass_rate": 0.0, "mean_coverage": 0.0, "mrr": 0.0}
    return {
        "case_count": len(results),
        "passed_count": sum(result.passed for result in results),
        "pass_rate": sum(result.passed for result in results) / len(results),
        "mean_coverage": sum(result.document_coverage for result in results) / len(results),
        "mrr": sum(result.reciprocal_rank for result in results) / len(results),
    }
