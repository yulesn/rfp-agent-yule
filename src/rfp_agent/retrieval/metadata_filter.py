"""문서 단위 조건 검색 (메타데이터 DataFrame).

- 역할: 기관, 예산 범위, 마감일, 키워드로 공고 목록을 좁힌다.
- 계약: filter_documents(df, ...) -> DataFrame (조건은 모두 AND, None 인 조건은 무시)
- 소속: Phase 1, ADR 0003 (SQL 대신 pandas).
"""

from datetime import datetime

import pandas as pd


def filter_documents(
    df: pd.DataFrame,
    agency: str | None = None,
    min_budget: int | None = None,
    max_budget: int | None = None,
    deadline_before: datetime | None = None,
    deadline_after: datetime | None = None,
    keyword: str | None = None,
) -> pd.DataFrame:
    """조건에 맞는 행만 남긴 DataFrame 을 반환한다."""
    # TODO: 컬럼명은 load_metadata 정규화 결과에 맞춰 구현 (agency 는 부분 일치)
    raise NotImplementedError
