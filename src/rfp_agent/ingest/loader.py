"""문서 로더 (확장자별 디스패치 + 파일 단위 격리).

- 역할: 파일 확장자에 맞는 파서를 호출하고 메타데이터를 붙인다.
- 계약:
  - load_document(path) -> RfpDocument  (.pdf / .hwp / .hwpx, 그 외는 ValueError)
  - parse_isolated(path, timeout_sec) -> RfpDocument  (별도 프로세스 + 제한 시간, 실패 시 ParseFailed)
  - load_all(raw_dir, metadata_df, timeout_sec, workers) -> list[RfpDocument]  (doc_id 로 메타데이터 병합)
  - load_all_with_report(...) -> (문서 리스트, 실패 리스트)
- 파싱 실패(에러/타임아웃)는 로그로 남기고 건너뛴다. 파일명은 NFC 로 정규화해 메타데이터와 맞춘다.
- 소속: Phase 1, ADR 0005.
"""

import logging
import subprocess
import sys
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from rfp_agent.ingest.naming import make_doc_id, normalize_name
from rfp_agent.ingest.schema import RfpDocument

logger = logging.getLogger(__name__)

SUPPORTED_SUFFIXES = {".pdf", ".hwp", ".hwpx"}
DEFAULT_WORKER_CMD = [sys.executable, "-m", "rfp_agent.ingest.worker"]


class ParseFailed(Exception):
    """파싱 실패. kind 는 "timeout" 또는 "error"."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(f"{kind}: {message}")
        self.kind = kind
        self.message = message


@dataclass
class FailureRecord:
    """실패한 파일 1건의 기록."""

    file_name: str
    kind: str
    message: str


def load_document(path: str | Path) -> RfpDocument:
    """확장자에 따라 parse_pdf / parse_hwp 로 분기한다 (현재 프로세스에서 실행)."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from rfp_agent.ingest.pdf import parse_pdf

        return parse_pdf(path)
    if suffix in (".hwp", ".hwpx"):
        from rfp_agent.ingest.hwp import parse_hwp

        return parse_hwp(path)
    raise ValueError(f"지원하지 않는 확장자입니다: {path.name}")


def parse_isolated(
    path: str | Path, timeout_sec: float, worker_cmd: list[str] | None = None
) -> RfpDocument:
    """파일 1개를 별도 프로세스에서 파싱한다. 제한 시간을 넘기거나 실패하면 ParseFailed.

    worker_cmd 는 테스트용 주입 지점이다 (기본은 `python -m rfp_agent.ingest.worker`).
    """
    cmd = list(worker_cmd or DEFAULT_WORKER_CMD)
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "doc.json"
        try:
            proc = subprocess.run(
                [*cmd, str(path), str(out)],
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
        except subprocess.TimeoutExpired as e:
            raise ParseFailed("timeout", f"{timeout_sec}초 안에 끝나지 않음") from e
        if proc.returncode != 0 or not out.exists():
            tail = (proc.stderr or "").strip().splitlines()[-1:] or ["(stderr 없음)"]
            raise ParseFailed("error", f"exit={proc.returncode} {tail[0][:200]}")
        return RfpDocument.model_validate_json(out.read_text(encoding="utf-8"))


def _json_safe(value: Any) -> Any:
    """pandas 값(NA/NaT/Timestamp/numpy 정수)을 JSON 으로 쓸 수 있는 값으로 바꾼다."""
    if value is None or value is pd.NA or value is pd.NaT:
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if hasattr(value, "item"):  # numpy 스칼라
        return value.item()
    return value


def metadata_for(metadata_df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """doc_id → 메타데이터 dict (JSON 안전). doc_id/file_name 컬럼은 제외한다."""
    out: dict[str, dict[str, Any]] = {}
    for row in metadata_df.to_dict(orient="records"):
        doc_id = row.pop("doc_id")
        row.pop("file_name", None)
        out[doc_id] = {k: _json_safe(v) for k, v in row.items()}
    return out


def list_documents(raw_dir: str | Path) -> list[Path]:
    """raw_dir 안의 지원 확장자 파일을 이름순(NFC)으로 돌려준다."""
    files = [
        p for p in Path(raw_dir).iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    ]
    return sorted(files, key=lambda p: normalize_name(p.name))


def load_all_with_report(
    raw_dir: str | Path,
    metadata_df: pd.DataFrame,
    timeout_sec: float = 60,
    workers: int = 4,
    worker_cmd: list[str] | None = None,
    progress: Callable[[int, int, str], None] | None = None,
    timeout_by_ext: dict[str, float] | None = None,
) -> tuple[list[RfpDocument], list[FailureRecord]]:
    """raw_dir 의 모든 문서를 파일별 프로세스로 파싱하고 메타데이터를 붙인다.

    timeout_by_ext 는 확장자(점 없이, 예: {"pdf": 300})별 제한 시간으로 timeout_sec 보다 우선한다.
    """
    overrides = {k.lower().lstrip("."): v for k, v in (timeout_by_ext or {}).items()}
    meta = metadata_for(metadata_df)
    files = list_documents(raw_dir)

    def work(path: Path) -> tuple[RfpDocument | None, FailureRecord | None]:
        name = normalize_name(path.name)
        try:
            limit = overrides.get(path.suffix.lower().lstrip("."), timeout_sec)
            doc = parse_isolated(path, limit, worker_cmd)
        except ParseFailed as e:
            logger.warning("파싱 실패: %s (%s)", name, e)
            return None, FailureRecord(name, e.kind, e.message)
        doc.metadata = meta.get(doc.doc_id, {})
        if doc.doc_id not in meta:
            logger.warning("메타데이터에 없는 문서: %s", name)
        return doc, None

    docs: list[RfpDocument] = []
    failures: list[FailureRecord] = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        for i, (doc, fail) in enumerate(pool.map(work, files), start=1):
            if doc is not None:
                docs.append(doc)
            if fail is not None:
                failures.append(fail)
            if progress:
                progress(i, len(files), normalize_name(files[i - 1].name))

    found = {make_doc_id(p.name) for p in files}
    for doc_id in sorted(set(meta) - found):
        logger.warning("파일이 없는 메타데이터 행: %s", doc_id)
    return docs, failures


def load_all(
    raw_dir: str | Path,
    metadata_df: pd.DataFrame,
    timeout_sec: float = 60,
    workers: int = 4,
    worker_cmd: list[str] | None = None,
) -> list[RfpDocument]:
    """raw_dir 의 모든 문서를 읽어 메타데이터를 붙여 반환한다 (실패 파일은 건너뜀)."""
    docs, _ = load_all_with_report(raw_dir, metadata_df, timeout_sec, workers, worker_cmd)
    return docs
