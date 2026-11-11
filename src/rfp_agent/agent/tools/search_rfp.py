"""도구: RFP 본문 검색 (RAG).

- 계약: search_rfp(query, doc_id=None) -> 출처 포함 텍스트 (문서명, 페이지, 본문 조각)
- 소속: Phase 1.
"""

from langchain_core.tools import tool


@tool
def search_rfp(query: str, doc_id: str | None = None) -> str:
    """RFP(제안요청서) 문서 본문에서 질문과 관련된 내용을 검색합니다.

    사업 요구사항, 제안서 작성 방법, 평가 기준, 제출 서류, 사업 기간처럼
    문서 안에 서술된 내용을 찾을 때 사용하세요.
    예산 범위나 마감일 같은 조건으로 공고 목록을 좁히려면 filter_rfps 를 쓰세요.

    Args:
        query: 찾고 싶은 내용을 담은 한국어 검색 문장. 핵심 키워드를 포함하세요.
        doc_id: 특정 문서 안에서만 찾고 싶을 때 문서 ID(파일명에서 확장자를 뺀 값). 생략하면 전체 검색.

    Returns:
        검색된 본문 조각 목록. 각 조각에 문서명과 페이지 출처가 붙어 있으며,
        답변할 때 이 출처를 인용해야 합니다.
    """
    # TODO: retriever.search 호출 후 "[문서명 p.N] 본문" 형태로 포맷
    raise NotImplementedError
