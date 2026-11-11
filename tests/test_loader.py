"""로더 테스트: 디스패치, 메타데이터 병합, 타임아웃/실패 처리 (가짜 워커 사용)."""

import sys
import textwrap
from pathlib import Path

import pandas as pd
import pytest

from rfp_agent.ingest.loader import (
    ParseFailed,
    list_documents,
    load_all_with_report,
    load_document,
    metadata_for,
    parse_isolated,
)

# 가짜 워커: argv = [<path>, <out_json>] 을 받아 문서를 쓴다. 이름에 'slow' 가 있으면 오래 잔다, 'bad' 면 실패.
FAKE_WORKER = textwrap.dedent(
    """
    import json, sys, time
    from pathlib import Path
    path, out = Path(sys.argv[1]), sys.argv[2]
    if "slow" in path.name:
        time.sleep(30)
    if "bad" in path.name:
        sys.stderr.write("boom\\n")
        sys.exit(3)
    doc = {"doc_id": path.stem.strip(), "file_name": path.name, "file_type": path.suffix[1:],
           "text": "본문", "pages": None, "metadata": {}}
    Path(out).write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    """
)


@pytest.fixture
def worker_cmd(tmp_path: Path) -> list[str]:
    script = tmp_path / "fake_worker.py"
    script.write_text(FAKE_WORKER, encoding="utf-8")
    return [sys.executable, str(script)]


def _raw(tmp_path: Path, names: list[str]) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    for n in names:
        (raw / n).write_bytes(b"x")
    return raw


def test_load_document_rejects_unknown_extension(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("x")
    with pytest.raises(ValueError):
        load_document(f)


def test_list_documents_filters_extensions(tmp_path: Path) -> None:
    raw = _raw(tmp_path, ["a.hwp", "b.PDF", "c.hwpx", "data_list.csv"])
    assert [p.name for p in list_documents(raw)] == ["a.hwp", "b.PDF", "c.hwpx"]


def test_parse_isolated_success(tmp_path: Path, worker_cmd: list[str]) -> None:
    raw = _raw(tmp_path, ["ok.hwp"])
    doc = parse_isolated(raw / "ok.hwp", 20, worker_cmd)
    assert doc.doc_id == "ok" and doc.text == "본문"


def test_parse_isolated_timeout(tmp_path: Path, worker_cmd: list[str]) -> None:
    raw = _raw(tmp_path, ["slow.hwp"])
    with pytest.raises(ParseFailed) as e:
        parse_isolated(raw / "slow.hwp", 1, worker_cmd)
    assert e.value.kind == "timeout"


def test_parse_isolated_error(tmp_path: Path, worker_cmd: list[str]) -> None:
    raw = _raw(tmp_path, ["bad.hwp"])
    with pytest.raises(ParseFailed) as e:
        parse_isolated(raw / "bad.hwp", 20, worker_cmd)
    assert e.value.kind == "error" and "boom" in e.value.message


def test_load_all_failures_not_fatal_and_metadata_attached(tmp_path: Path, worker_cmd: list[str]) -> None:
    raw = _raw(tmp_path, ["ok1.hwp", "slow1.hwp", "bad1.hwp", "ok2.pdf"])
    meta = pd.DataFrame(
        {
            "doc_id": ["ok1", "ok2", "ghost"],
            "file_name": ["ok1.hwp", "ok2.pdf", "ghost.hwp"],
            "title": ["사업1", "사업2", "유령"],
            "amount": pd.array([1000, None, 5], dtype="Int64"),
            "bid_end": pd.to_datetime(["2024-10-15 17:00:00", None, None]),
        }
    )
    docs, failures = load_all_with_report(raw, meta, timeout_sec=2, workers=2, worker_cmd=worker_cmd)
    assert sorted(d.doc_id for d in docs) == ["ok1", "ok2"]
    assert sorted((f.file_name, f.kind) for f in failures) == [("bad1.hwp", "error"), ("slow1.hwp", "timeout")]
    by_id = {d.doc_id: d for d in docs}
    assert by_id["ok1"].metadata == {"title": "사업1", "amount": 1000, "bid_end": "2024-10-15T17:00:00"}
    assert by_id["ok2"].metadata["amount"] is None and by_id["ok2"].metadata["bid_end"] is None


def test_metadata_for_is_json_safe() -> None:
    df = pd.DataFrame(
        {"doc_id": ["a"], "file_name": ["a.hwp"], "amount": pd.array([7], dtype="Int64"),
         "bid_end": pd.to_datetime(["2024-01-02"])}
    )
    m = metadata_for(df)["a"]
    assert m == {"amount": 7, "bid_end": "2024-01-02T00:00:00"}
    assert type(m["amount"]) is int


def test_timeout_by_extension(tmp_path: Path, worker_cmd: list[str]) -> None:
    raw = _raw(tmp_path, ["a.pdf", "slow_b.hwp"])
    meta = pd.DataFrame({"doc_id": ["a"], "file_name": ["a.pdf"]})
    docs, failures = load_all_with_report(
        raw, meta, timeout_sec=1, workers=2, worker_cmd=worker_cmd, timeout_by_ext={"pdf": 20}
    )
    assert [d.doc_id for d in docs] == ["a"]
    assert [(f.file_name, f.kind) for f in failures] == [("slow_b.hwp", "timeout")]
