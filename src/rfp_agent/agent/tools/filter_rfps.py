"""도구: 메타데이터 조건으로 공고 목록 필터링.

- 계약: filter_rfps(...) -> 조건에 맞는 공고 목록 문자열 (doc_id, 사업명, 기관, 예산, 마감일)
- 소속: Phase 1, ADR 0003.
"""

from langchain_core.tools import tool


@tool
def filter_rfps(
    agency: str | None = None,
    min_budget: int | None = None,
    max_budget: int | None = None,
    deadline_before: str | None = None,
    deadline_after: str | None = None,
    keyword: str | None = None,
) -> str:
    """발주기관, 예산 범위, 마감일, 키워드 같은 조건으로 RFP 공고 목록을 찾습니다.

    "예산이 5억 원 이상인 공고", "12월 안에 마감되는 공고"처럼 문서 단위 조건 질문에 사용하세요.
    문서 본문의 상세 내용은 이 도구로 알 수 없으니 search_rfp 를 쓰세요.
    모든 조건은 AND 로 결합되며, 주지 않은 조건은 무시됩니다.

    Args:
        agency: 발주기관 이름 (부분 일치).
        min_budget: 최소 예산(원 단위 정수).
        max_budget: 최대 예산(원 단위 정수).
        deadline_before: 이 날짜(YYYY-MM-DD) 이전에 마감되는 공고.
        deadline_after: 이 날짜(YYYY-MM-DD) 이후에 마감되는 공고.
        keyword: 사업명 등에 포함된 키워드.

    Returns:
        조건에 맞는 공고 목록 (문서 ID, 사업명, 발주기관, 예산, 마감일).
    """
    # TODO: 메타데이터 DataFrame 로드, 날짜 문자열 파싱, metadata_filter.filter_documents 호출
    raise NotImplementedError
