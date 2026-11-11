"""수집 단계의 공통 데이터 모델.

- 역할: 파서/청킹/검색이 주고받는 pydantic 모델 정의.
- 계약: RfpDocument(문서 1건), PageText(페이지 단위 텍스트), Chunk(검색 단위).
  doc_id 는 파일명 stem 이며 메타데이터 CSV 와의 조인 키다.
- 소속: Phase 1.
"""

from typing import Any

from pydantic import BaseModel, Field


class PageText(BaseModel):
    """한 페이지의 텍스트. page 는 1부터 시작한다."""

    page: int
    text: str


class RfpDocument(BaseModel):
    """파싱된 RFP 문서 1건."""

    doc_id: str
    file_name: str
    file_type: str  # "pdf" | "hwp" | "hwpx"
    text: str
    pages: list[PageText] | None = None  # 페이지 구분이 없는 형식(hwp 등)은 None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Chunk(BaseModel):
    """검색 단위 청크. 출처 인용을 위해 metadata 에 page 등을 담는다."""

    chunk_id: str
    doc_id: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
