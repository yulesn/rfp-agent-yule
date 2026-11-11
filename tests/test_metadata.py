"""메타데이터 로더 정규화 테스트 (합성 CSV)."""

import unicodedata
from pathlib import Path

import pandas as pd

from rfp_agent.ingest.metadata import load_metadata
from rfp_agent.ingest.naming import make_doc_id

HEADER = "공고 번호,공고 차수,사업명,사업 금액,발주 기관,공개 일자,입찰 참여 시작일,입찰 참여 마감일,사업 요약,파일형식,파일명,텍스트\n"


def _write(tmp_path: Path, rows: list[str]) -> Path:
    p = tmp_path / "meta.csv"
    p.write_text("﻿" + HEADER + "\n".join(rows) + "\n", encoding="utf-8")
    return p


def test_normalization(tmp_path: Path) -> None:
    nfd = unicodedata.normalize("NFD", "기관_사업 .hwp")
    rows = [
        f"20240001,0.0,사업A,130000000.0,기관A,2024-10-04 13:51:23,,2024-10-15 17:00:00,요약,hwp,{nfd},목차",
        ",,사업B,0.0,기관B,2024-10-05 10:00:00,2024-10-06 09:00:00,,요약,pdf,기관B_사업B.pdf,목차",
        ",,사업C,,기관C,2024-10-05 10:00:00,,,요약,hwp,기관C_사업C.hwp,목차",
    ]
    df = load_metadata(_write(tmp_path, rows))

    assert "텍스트" not in df.columns and "file_type" not in df.columns
    assert list(df["doc_id"]) == ["기관_사업", "기관B_사업B", "기관C_사업C"]
    assert df.loc[0, "file_name"] == unicodedata.normalize("NFC", nfd)  # NFC 정규화
    assert df.loc[0, "amount"] == 130000000
    assert pd.isna(df.loc[1, "amount"]) and pd.isna(df.loc[2, "amount"])  # 0 / 빈 값 → NA
    assert str(df["amount"].dtype) == "Int64"
    assert df.loc[0, "notice_id"] == "20240001" and pd.isna(df.loc[1, "notice_id"])
    assert pd.isna(df.loc[0, "bid_start"]) and pd.isna(df.loc[0, "bid_start"])
    assert df.loc[0, "bid_end"] == pd.Timestamp("2024-10-15 17:00:00")
    assert pd.isna(df.loc[1, "bid_end"])
    assert str(df["bid_end"].dtype).startswith("datetime64")


def test_doc_id_matches_file_name_nfd_and_nfc() -> None:
    nfc = "한글_문서 .hwp"
    nfd = unicodedata.normalize("NFD", nfc)
    assert make_doc_id(nfd) == make_doc_id(nfc) == "한글_문서"
