"""메타데이터 CSV 로더.

- 역할: 공고 메타데이터(기관, 예산, 마감일 등)를 DataFrame 으로 읽는다.
- 계약: load_metadata(path) -> pandas.DataFrame
  - 예산은 int(원) 으로, 마감일 등 날짜는 datetime 으로 정규화한다.
  - doc_id 컬럼 = 파일명 stem (RfpDocument.doc_id 와 조인 키).
- 소속: Phase 1, ADR 0003 (문서 단위 조건 검색은 pandas).
"""

from pathlib import Path

import pandas as pd


def load_metadata(path: str | Path) -> pd.DataFrame:
    """메타데이터 CSV 를 정규화된 DataFrame 으로 읽는다."""
    # TODO: 실제 컬럼 확인(scripts/inspect_data.py) 후 컬럼명 매핑, 금액/날짜 정규화
    raise NotImplementedError
