"""HWP/HWPX 파서.

- 역할: 한글 문서에서 텍스트를 추출한다.
- 계약: parse_hwp(path) -> RfpDocument (file_type 은 확장자에 따라 "hwp"/"hwpx").
- 소속: Phase 1 (플랜 3절 4번). Phase 1 후보는 hwp-hwpx-parser.
  대안: pyhwp 의 hwp5html(표 HTML 보존), LibreOffice 로 PDF 변환 후 PDF 파이프라인 재사용.
  세 후보 비교는 Phase 5.
"""

from pathlib import Path

from rfp_agent.ingest.schema import RfpDocument


def parse_hwp(path: str | Path) -> RfpDocument:
    """HWP/HWPX 를 RfpDocument 로 변환한다."""
    # TODO: hwp-hwpx-parser 사용법 확인 후 구현 (텍스트만, 표는 Phase 5)
    raise NotImplementedError
