"""문서 로더 (확장자별 디스패치).

- 역할: 파일 확장자에 맞는 파서를 호출하고 메타데이터를 붙인다.
- 계약:
  - load_document(path) -> RfpDocument  (.pdf / .hwp / .hwpx, 그 외는 ValueError)
  - load_all(raw_dir, metadata_df) -> list[RfpDocument]  (doc_id 로 메타데이터 병합)
- 소속: Phase 1.
"""

from pathlib import Path

import pandas as pd

from rfp_agent.ingest.schema import RfpDocument


def load_document(path: str | Path) -> RfpDocument:
    """확장자에 따라 parse_pdf / parse_hwp 로 분기한다."""
    # TODO: 확장자 매핑 후 parse_pdf / parse_hwp 호출
    raise NotImplementedError


def load_all(raw_dir: str | Path, metadata_df: pd.DataFrame) -> list[RfpDocument]:
    """raw_dir 의 모든 문서를 읽어 메타데이터를 붙여 반환한다."""
    # TODO: 파일 순회, 파싱 실패는 로그 남기고 건너뛰기, metadata_df 와 doc_id 조인
    raise NotImplementedError
