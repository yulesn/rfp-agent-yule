"""검색 지표.

- 역할: 검색 결과가 정답 문서를 얼마나 잘 찾았는지 계산한다.
- 계약: 입력은 검색된 doc_id 순위 리스트와 정답 doc_id 집합.
- 소속: Phase 2 (플랜 2절 Phase 2-2).
"""


def hit_at_k(retrieved_ids: list[str], answer_ids: set[str], k: int) -> float:
    """상위 k 개 안에 정답이 하나라도 있으면 1.0, 아니면 0.0."""
    # TODO: 구현
    raise NotImplementedError


def mrr(retrieved_ids: list[str], answer_ids: set[str]) -> float:
    """첫 정답의 순위 역수 (정답이 없으면 0.0)."""
    # TODO: 구현
    raise NotImplementedError
