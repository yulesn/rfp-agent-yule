"""데이터 탐색 스크립트.

- 역할: data/raw 의 파일 형식 비율, 파일 크기, PDF 페이지 수, 스캔 PDF 의심 여부,
  HWP 파싱 가능 여부(글자 수/표 개수/에러), 메타데이터 CSV 요약, 메타데이터↔파일 매칭을 점검한다.
- 사용: uv run python scripts/inspect_data.py --config configs/default.yaml
- 출력: data/processed/inspect_report.json + 콘솔 한국어 요약 (문서 본문은 출력하지 않는다).
- 소속: Phase 1 (플랜 2절 Phase 1-1).
"""

import argparse
import hashlib
import json
import multiprocessing as mp
import sys
import time
import unicodedata
import warnings
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from rfp_agent.config import load_config

COPY_MARK = "의 사본"
# 스캔 PDF 의심 기준: 페이지당 평균 글자 수가 이 값 미만이면 의심
SCAN_AVG_CHARS_PER_PAGE = 50
# 글자가 이 값 미만인 페이지가 전체의 이 비율 이상이면 의심
SCAN_EMPTY_PAGE_CHARS = 20
SCAN_EMPTY_PAGE_RATIO = 0.5
# hwp-hwpx-parser 가 일부 파일에서 무한 루프에 빠지므로 파일당 제한 시간을 둔다
HWP_TIMEOUT_SEC = 60


def nfc(s: str) -> str:
    """macOS 파일명(NFD)과 CSV(NFC) 비교를 위해 정규화한다."""
    return unicodedata.normalize("NFC", s)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def original_name(name: str) -> str:
    """'xxx.hwp의 사본' / 'xxx.pdf의 사본.pdf' → 'xxx.hwp' / 'xxx.pdf'."""
    name = nfc(name)
    if COPY_MARK not in name:
        return name
    return name.split(COPY_MARK)[0]


def kind_of(name: str) -> str:
    base = original_name(name).lower()  # original_name 이 NFC 정규화까지 한다
    for ext in ("hwpx", "hwp", "pdf"):
        if base.endswith("." + ext):
            return ext
    return Path(base).suffix.lstrip(".") or "(none)"


def inspect_pdf(path: Path) -> dict[str, Any]:
    import pymupdf

    out: dict[str, Any] = {}
    try:
        with pymupdf.open(path) as doc:
            chars = [len(page.get_text("text").strip()) for page in doc]
            images = [len(page.get_images()) for page in doc]
            tables = 0
            table_failures = 0
            for page in doc:
                try:
                    tables += len(page.find_tables().tables)
                except Exception:  # noqa: BLE001 - 표 탐지 실패는 개수만 세어 기록
                    table_failures += 1
        n = len(chars)
        avg = sum(chars) / n if n else 0
        empty = sum(1 for c in chars if c < SCAN_EMPTY_PAGE_CHARS)
        out = {
            "pages": n,
            "chars_total": sum(chars),
            "chars_avg_per_page": round(avg, 1),
            "empty_pages": empty,
            "pages_with_images": sum(1 for i in images if i),
            "tables_detected": tables,
            "table_detect_failed_pages": table_failures,
            "scanned_suspect": bool(
                n and (avg < SCAN_AVG_CHARS_PER_PAGE or empty / n >= SCAN_EMPTY_PAGE_RATIO)
            ),
        }
    except Exception as e:  # noqa: BLE001
        out = {"error": f"{type(e).__name__}: {e}"[:300]}
    return out


def _hwp_worker(path: str, q: "mp.Queue[dict[str, Any]]") -> None:
    q.put(_inspect_hwp_inner(Path(path)))


def inspect_hwp(path: Path) -> dict[str, Any]:
    """별도 프로세스에서 실행해 파서가 멈춰도 전체 탐색이 멈추지 않게 한다."""
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    proc = ctx.Process(target=_hwp_worker, args=(str(path), q))
    t0 = time.perf_counter()
    proc.start()
    proc.join(HWP_TIMEOUT_SEC)
    if proc.is_alive():
        proc.kill()
        proc.join()
        return {
            "opens": False,
            "error": f"Timeout: {HWP_TIMEOUT_SEC}초 안에 끝나지 않음 (파서 무한 루프 의심)",
            "timeout": True,
            "seconds": round(time.perf_counter() - t0, 2),
        }
    try:
        return q.get(timeout=5)
    except Exception:  # noqa: BLE001
        return {"opens": False, "error": f"프로세스 비정상 종료 exit={proc.exitcode}"}


def _inspect_hwp_inner(path: Path) -> dict[str, Any]:
    from hwp_hwpx_parser import Reader

    t0 = time.perf_counter()
    try:
        with Reader(path) as r:
            text = r.text
            tables = r.tables
            return {
                "opens": True,
                "file_type": str(r.file_type),
                "encrypted": bool(r.is_encrypted),
                "chars": len(text),
                "chars_no_ws": len("".join(text.split())),
                "tables": len(tables),
                "seconds": round(time.perf_counter() - t0, 2),
            }
    except Exception as e:  # noqa: BLE001
        return {
            "opens": False,
            "error": f"{type(e).__name__}: {e}"[:300],
            "seconds": round(time.perf_counter() - t0, 2),
        }


def inspect_metadata(df: pd.DataFrame) -> dict[str, Any]:
    cols = []
    for c in df.columns:
        s = df[c]
        samples = [str(v)[:60] for v in s.dropna().head(3)]
        cols.append(
            {
                "name": c,
                "dtype": str(s.dtype),
                "null_ratio": round(float(s.isna().mean()), 3),
                "n_unique": int(s.nunique(dropna=True)),
                "samples": samples,
            }
        )
    extra: dict[str, Any] = {}
    if "사업 금액" in df:
        extra["amount_describe"] = {k: float(v) for k, v in df["사업 금액"].describe().items()}
    for c in ("공개 일자", "입찰 참여 시작일", "입찰 참여 마감일"):
        if c in df:
            d = pd.to_datetime(df[c], errors="coerce")
            extra[f"{c}_range"] = [str(d.min()), str(d.max())]
    if "발주 기관" in df:
        extra["top_agencies"] = df["발주 기관"].value_counts().head(5).to_dict()
    if "공고 번호" in df:
        extra["notice_id_duplicated_rows"] = int(df["공고 번호"].dropna().duplicated().sum())
    if "공고 차수" in df:
        extra["notice_round_values"] = df["공고 차수"].value_counts(dropna=False).to_dict()
    if "텍스트" in df:
        lens = df["텍스트"].fillna("").str.len()
        extra["csv_text_chars"] = {k: float(v) for k, v in lens.describe().items()}
    if "사업 요약" in df:
        extra["summary_chars_mean"] = float(df["사업 요약"].fillna("").str.len().mean())
    return {"rows": len(df), "columns": cols, "extra": extra}


def main() -> None:
    parser = argparse.ArgumentParser(description="RFP 데이터 탐색")
    parser.add_argument("--config", default="configs/default.yaml")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    cfg = load_config(args.config)
    raw_dir = Path(cfg["paths"]["raw_dir"])
    meta_path = Path(cfg["paths"]["metadata_file"])
    out_dir = Path(cfg["paths"]["processed_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1) 파일 목록 / 사본 판별
    entries = sorted(p for p in raw_dir.iterdir() if p.is_file() and p != meta_path)
    # macOS 파일명은 NFD 라 반드시 NFC 로 정규화한 뒤 비교한다 (docs/trials 참고)
    originals = [p for p in entries if COPY_MARK not in nfc(p.name)]
    copies = [p for p in entries if COPY_MARK in nfc(p.name)]
    by_name = {nfc(p.name): p for p in originals}

    copy_info = {"count": len(copies), "identical_to_original": 0, "differs": [], "no_original": []}
    for c in copies:
        o = by_name.get(original_name(c.name))
        if o is None:
            copy_info["no_original"].append(c.name)
        elif c.stat().st_size == o.stat().st_size and sha256(c) == sha256(o):
            copy_info["identical_to_original"] += 1
        else:
            copy_info["differs"].append(c.name)

    ext_all = Counter(kind_of(p.name) for p in entries)
    ext_orig = Counter(kind_of(p.name) for p in originals)

    # ---- 2) 원본 파일 상세 분석
    files: list[dict[str, Any]] = []
    for i, p in enumerate(originals, 1):
        kind = kind_of(p.name)
        print(f"[{i}/{len(originals)}] {kind} {p.name[:40]}", file=sys.stderr, flush=True)
        rec: dict[str, Any] = {
            "name": p.name,
            "kind": kind,
            "size_mb": round(p.stat().st_size / 1e6, 3),
        }
        if kind == "pdf":
            rec.update(inspect_pdf(p))
        elif kind in ("hwp", "hwpx"):
            rec.update(inspect_hwp(p))
        files.append(rec)

    # ---- 3) 메타데이터
    df = pd.read_csv(meta_path, encoding="utf-8-sig")
    meta = inspect_metadata(df)

    # ---- 4) 매칭 (NFC 정규화 후 파일명 완전 일치)
    file_names = {nfc(p.name): p.name for p in originals}
    csv_names = {nfc(str(n)) for n in df["파일명"].dropna()}
    csv_names_list = [nfc(str(n)) for n in df["파일명"].dropna()]
    matched = csv_names & set(file_names)
    csv_only = sorted(csv_names - set(file_names))
    file_only = sorted(set(file_names) - csv_names)

    # 파일명 공백/확장자 차이로 어긋난 경우 대비: 확장자 제거 + 공백 제거 후 재비교
    def loose(s: str) -> str:
        return "".join(Path(s).stem.split())

    loose_files = {loose(n): n for n in file_names}
    loose_rescued = [n for n in csv_only if loose(n) in loose_files]
    matching = {
        "metadata_rows": len(df),
        "metadata_unique_filenames": len(csv_names),
        "metadata_filename_duplicates": len(csv_names_list) - len(csv_names),
        "original_files": len(originals),
        "matched": len(matched),
        "csv_without_file": csv_only,
        "file_without_csv": file_only,
        "csv_without_file_rescued_by_loose_match": loose_rescued,
        "csv_format_vs_actual_ext_mismatch": [
            n
            for n, k in zip(df["파일명"].astype(str), df["파일형식"].astype(str), strict=False)
            if kind_of(n) != k
        ],
    }

    # CSV 의 '텍스트' 컬럼과 파서 추출 글자 수 비교 (CSV 에 이미 본문이 들어 있는지 확인)
    ratios = []
    csv_text_len = {nfc(str(r["파일명"])): len(str(r["텍스트"])) for _, r in df.iterrows()}
    for f in files:
        key = nfc(f["name"])
        n_csv = csv_text_len.get(key)
        n_parsed = f.get("chars") or f.get("chars_total")
        if n_csv and n_parsed:
            f["csv_text_chars"] = n_csv
            f["parsed_vs_csv_ratio"] = round(n_parsed / n_csv, 2)
            ratios.append(n_parsed / n_csv)

    # ---- 5) 집계
    hwp_files = [f for f in files if f["kind"] in ("hwp", "hwpx")]
    pdf_files = [f for f in files if f["kind"] == "pdf"]
    hwp_ok = [f for f in hwp_files if f.get("opens")]
    hwp_fail = [f for f in hwp_files if not f.get("opens")]
    hwp_empty = [f for f in hwp_ok if f["chars_no_ws"] < 500]
    summary = {
        "files_total": len(entries),
        "originals": len(originals),
        "ext_all": dict(ext_all),
        "ext_originals": dict(ext_orig),
        "size_mb_total_originals": round(sum(f["size_mb"] for f in files), 1),
        "size_mb_max": max((f["size_mb"] for f in files), default=0),
        "size_mb_median": float(pd.Series([f["size_mb"] for f in files]).median()),
        "pdf_count": len(pdf_files),
        "pdf_pages_total": sum(f.get("pages", 0) for f in pdf_files),
        "pdf_scanned_suspects": [f["name"] for f in pdf_files if f.get("scanned_suspect")],
        "pdf_errors": [f["name"] for f in pdf_files if "error" in f],
        "hwp_count": len(hwp_files),
        "hwp_open_ok": len(hwp_ok),
        "hwp_open_fail": [{"name": f["name"], "error": f["error"]} for f in hwp_fail],
        "hwp_low_text_files": [f["name"] for f in hwp_empty],
        "hwp_chars_median": float(pd.Series([f["chars"] for f in hwp_ok]).median())
        if hwp_ok
        else 0,
        "hwp_tables_total": sum(f["tables"] for f in hwp_ok),
        "hwp_tables_median": float(pd.Series([f["tables"] for f in hwp_ok]).median())
        if hwp_ok
        else 0,
        "parsed_vs_csv_ratio_median": float(pd.Series(ratios).median()) if ratios else None,
    }

    report = {
        "summary": summary,
        "copies": copy_info,
        "metadata": meta,
        "matching": matching,
        "files": files,
    }
    out_path = out_dir / "inspect_report.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print_summary(report, out_path)


def print_summary(report: dict[str, Any], out_path: Path) -> None:
    s, c, m, mt = report["summary"], report["copies"], report["metadata"], report["matching"]
    print("=" * 60)
    print("RFP 데이터 탐색 요약")
    print("=" * 60)
    print(f"[파일] 전체 {s['files_total']}개 (확장자별: {s['ext_all']})")
    print(
        f"  - '의 사본' {c['count']}개 중 원본과 바이트 동일 {c['identical_to_original']}개,"
        f" 다름 {len(c['differs'])}개, 원본 없음 {len(c['no_original'])}개"
    )
    print(f"  - 사본 제외 원본 {s['originals']}개: {s['ext_originals']}")
    print(
        f"  - 원본 용량 합계 {s['size_mb_total_originals']}MB,"
        f" 중앙값 {s['size_mb_median']:.2f}MB, 최대 {s['size_mb_max']}MB"
    )
    print(f"[PDF] {s['pdf_count']}개, 총 {s['pdf_pages_total']}쪽")
    for f in report["files"]:
        if f["kind"] == "pdf":
            print(
                f"  - {f['name'][:30]}: {f.get('pages')}쪽, 쪽당 {f.get('chars_avg_per_page')}자,"
                f" 빈 쪽 {f.get('empty_pages')}, 표 {f.get('tables_detected')},"
                f" 스캔의심={f.get('scanned_suspect')}"
                + (f" 에러={f['error']}" if "error" in f else "")
            )
    print(f"  - 스캔 의심 PDF: {len(s['pdf_scanned_suspects'])}개")
    print(
        f"[HWP] {s['hwp_count']}개 중 열림 {s['hwp_open_ok']}개, 실패 {len(s['hwp_open_fail'])}개,"
        f" 글자 거의 없음 {len(s['hwp_low_text_files'])}개"
    )
    print(
        f"  - 글자 수 중앙값 {s['hwp_chars_median']:.0f}, 표 총 {s['hwp_tables_total']}개"
        f" (파일당 중앙값 {s['hwp_tables_median']:.0f})"
    )
    for f in s["hwp_open_fail"][:10]:
        print(f"  - 실패: {f['name'][:40]} → {f['error']}")
    print(f"  - 파서 추출 글자 / CSV '텍스트' 글자 비율 중앙값: {s['parsed_vs_csv_ratio_median']}")
    print(f"[메타데이터] {m['rows']}행, 컬럼 {len(m['columns'])}개")
    for col in m["columns"]:
        print(
            f"  - {col['name']} ({col['dtype']}): 결측 {col['null_ratio']:.0%},"
            f" 고유 {col['n_unique']}, 예: {col['samples'][:2]}"
        )
    print(
        f"[매칭] CSV {mt['metadata_rows']}행 ↔ 원본 파일 {mt['original_files']}개:"
        f" 일치 {mt['matched']}, CSV에만 {len(mt['csv_without_file'])},"
        f" 파일에만 {len(mt['file_without_csv'])}"
    )
    print(
        f"  - CSV 파일형식 컬럼과 실제 확장자 불일치: {len(mt['csv_format_vs_actual_ext_mismatch'])}건"
    )
    print(f"리포트 저장: {out_path}")


if __name__ == "__main__":
    main()
