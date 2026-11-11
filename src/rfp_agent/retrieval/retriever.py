"""청크 검색.

- 역할: 질문과 비슷한 청크를 점수와 함께 찾는다. Chroma 만 사용(ADR 0003).
- 계약: search(query, k, where) -> list[tuple[Chunk, float]]
  where 는 Chroma 메타데이터 필터(예: {"doc_id": "..."}), None 이면 전체 검색.
- 소속: Phase 1. 하이브리드/리랭크는 Phase 6.
"""

from typing import Any

from rfp_agent.ingest.schema import Chunk


def search(query: str, k: int, where: dict[str, Any] | None = None) -> list[tuple[Chunk, float]]:
    """상위 k 개 청크와 유사도 점수를 반환한다."""
    # TODO: 벡터스토어 핸들을 어디서 받을지 결정(인자 vs 모듈 캐시), similarity_search_with_score
    raise NotImplementedError
