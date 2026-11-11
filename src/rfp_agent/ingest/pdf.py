"""PDF 파서 (PyMuPDF).

- 역할: PDF 한 개를 페이지별 텍스트로 추출한다.
- 계약: parse_pdf(path) -> RfpDocument (pages 채움, file_type="pdf").
- 소속: Phase 1 (플랜 3절 5번). 표 많은 문서는 Phase 5에서 pymupdf4llm/Docling 비교.
"""

from pathlib import Path

from rfp_agent.ingest.schema import RfpDocument


def parse_pdf(path: str | Path) -> RfpDocument:
    """PDF 를 RfpDocument 로 변환한다."""
    # TODO: pymupdf(fitz) 를 함수 안에서 import, 페이지별 get_text() 후 PageText 리스트 구성
    raise NotImplementedError
