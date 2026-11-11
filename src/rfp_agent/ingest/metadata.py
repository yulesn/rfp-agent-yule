"""메타데이터 CSV 로더.

- 역할: 공고 메타데이터(기관, 예산, 마감일 등)를 DataFrame 으로 읽는다.
- 계약: load_metadata(path) -> pandas.DataFrame (행 = 문서 1건, doc_id 로 조인).
  - 인코딩 utf-8-sig(BOM). 파일명은 NFC 로 정규화, doc_id = 파일명 stem (ingest.naming.make_doc_id).
  - `텍스트` 컬럼은 대부분 목차라 버린다 (ADR 0004). 본문은 원본 파일을 직접 파싱한다.
  - `파일형식` 은 확장자와 중복이라 버린다.
  - 사업 금액은 Int64(원)이고 0 이나 빈 값은 <NA> (미공개/미정으로 취급). 날짜는 datetime64 이고 빈 값은 NaT.
  - 컬럼 이름 매핑(한글 → 영문):
    공고 번호=notice_id, 공고 차수=notice_round, 사업명=title, 사업 금액=amount, 발주 기관=agency,
    공개 일자=published_at, 입찰 참여 시작일=bid_start, 입찰 참여 마감일=bid_end, 사업 요약=summary,
    파일명=file_name. (`공고 번호` 는 18% 결측이라 키로 못 쓴다.)
- 소속: Phase 1, ADR 0003 (문서 단위 조건 검색은 pandas), ADR 0004.
"""

from pathlib import Path

import pandas as pd

from rfp_agent.ingest.naming import make_doc_id, normalize_name

COLUMN_MAP = {
    "공고 번호": "notice_id",
    "공고 차수": "notice_round",
    "사업명": "title",
    "사업 금액": "amount",
    "발주 기관": "agency",
    "공개 일자": "published_at",
    "입찰 참여 시작일": "bid_start",
    "입찰 참여 마감일": "bid_end",
    "사업 요약": "summary",
    "파일명": "file_name",
}
DATE_COLUMNS = ["published_at", "bid_start", "bid_end"]


def load_metadata(path: str | Path) -> pd.DataFrame:
    """메타데이터 CSV 를 정규화된 DataFrame 으로 읽는다."""
    raw = pd.read_csv(path, encoding="utf-8-sig", dtype={"공고 번호": "string"})
    df = raw[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)

    df["file_name"] = df["file_name"].map(normalize_name)
    df.insert(0, "doc_id", df["file_name"].map(make_doc_id))
    if df["doc_id"].duplicated().any():
        dup = df.loc[df["doc_id"].duplicated(), "doc_id"].tolist()
        raise ValueError(f"doc_id 가 중복됩니다: {dup[:3]}")

    df["notice_id"] = df["notice_id"].str.strip().replace("", pd.NA)
    df["notice_round"] = pd.to_numeric(df["notice_round"], errors="coerce").round().astype("Int64")
    amount = pd.to_numeric(df["amount"], errors="coerce").round().astype("Int64")
    df["amount"] = amount.mask(amount == 0)  # 0원 = 미공개/미정
    for col in DATE_COLUMNS:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ("title", "agency", "summary"):
        df[col] = df[col].astype("string").str.strip()
    return df.reset_index(drop=True)
