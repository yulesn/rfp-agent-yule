"""메타데이터 CSV 로더.

- 역할: 공고 메타데이터(기관, 예산, 마감일 등)를 DataFrame 으로 읽는다.
- 계약: load_metadata(path) -> pandas.DataFrame
  - 예산은 int(원) 으로, 마감일 등 날짜는 datetime 으로 정규화한다.
  - doc_id 컬럼 = 파일명 stem (RfpDocument.doc_id 와 조인 키). `공고 번호` 는 18% 결측이라 키로 못 쓴다.
  - `텍스트` 컬럼은 대부분 문서 목차라 읽을 때 버린다 (ADR 0004). 본문은 원본 파일을 직접 파싱한다.
  - `파일형식` 컬럼은 파일 확장자와 중복이므로 필요할 때만 유지한다.
- 소속: Phase 1, ADR 0003 (문서 단위 조건 검색은 pandas).
"""

from pathlib import Path

import pandas as pd


def load_metadata(path: str | Path) -> pd.DataFrame:
    """메타데이터 CSV 를 정규화된 DataFrame 으로 읽는다."""
    # TODO: 컬럼명 매핑(docs/research/2026-11-11-데이터-탐색.md 2절), 금액/날짜 정규화, '텍스트' 컬럼 제거
    raise NotImplementedError
