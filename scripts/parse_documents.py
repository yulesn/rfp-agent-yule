"""문서 파싱 + 청킹 CLI.

- 역할: data/raw 의 문서를 파싱(파일별 프로세스, 제한 시간)하고 청킹해서 data/processed 에 JSONL 로 저장한다.
- 사용: uv run python scripts/parse_documents.py --config configs/default.yaml
- 출력: data/processed/documents.jsonl, chunks.jsonl (커밋 금지). 요약은 콘솔에만 출력(본문은 출력하지 않음).
- 소속: Phase 1-2 (임베딩/Chroma 적재는 scripts/build_index.py 가 이어서 한다).
"""

import argparse
import json
import logging
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from rfp_agent.config import load_config
from rfp_agent.ingest.chunking import chunk_document
from rfp_agent.ingest.loader import load_all_with_report
from rfp_agent.ingest.metadata import load_metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="RFP 파싱 + 청킹")
    parser.add_argument("--config", default="configs/default.yaml")
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")

    cfg = load_config(args.config)
    paths, ing, chk = cfg["paths"], cfg["ingest"], cfg["chunking"]
    out_dir = Path(paths["processed_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_df = load_metadata(paths["metadata_file"])

    def progress(i: int, total: int, name: str) -> None:
        if i % 10 == 0 or i == total:
            print(f"  파싱 {i}/{total} (최근: {name[:30]})", file=sys.stderr, flush=True)

    t0 = time.perf_counter()
    docs, failures = load_all_with_report(
        paths["raw_dir"],
        meta_df,
        ing["timeout_sec"],
        ing["workers"],
        progress=progress,
        timeout_by_ext=ing.get("timeout_sec_by_ext"),
    )
    parse_sec = time.perf_counter() - t0

    chunks = []
    for doc in docs:
        chunks.extend(
            chunk_document(doc, chk["chunk_size"], chk["chunk_overlap"], chk.get("add_header", True))
        )

    with (out_dir / "documents.jsonl").open("w", encoding="utf-8") as f:
        for doc in docs:
            f.write(doc.model_dump_json() + "\n")
    with (out_dir / "chunks.jsonl").open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.model_dump_json() + "\n")

    print_summary(docs, failures, chunks, parse_sec, meta_df, ing, chk)
    report = {
        "docs_ok": len(docs),
        "docs_failed": [{"file": f.file_name, "kind": f.kind, "message": f.message} for f in failures],
        "chunks": len(chunks),
    }
    (out_dir / "parse_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


def print_summary(docs, failures, chunks, parse_sec, meta_df, ing, chk) -> None:  # type: ignore[no-untyped-def]
    print("=" * 60)
    print("파싱 + 청킹 요약")
    print("=" * 60)
    by_type = Counter(d.file_type for d in docs)
    print(f"[문서] 성공 {len(docs)}건 {dict(by_type)} / 실패 {len(failures)}건 / 메타데이터 {len(meta_df)}행")
    print(f"  - 파싱 소요 {parse_sec:.0f}초 (workers={ing['workers']}, timeout={ing['timeout_sec']}s)")
    for f in failures:
        print(f"  - 실패: {f.file_name[:40]} → {f.kind}: {f.message}")
    no_meta = [d.doc_id for d in docs if not d.metadata]
    print(f"  - 메타데이터가 붙지 않은 문서: {len(no_meta)}건")
    empty = [d.doc_id for d in docs if len(d.text.strip()) < 500]
    print(f"  - 본문 500자 미만 문서: {len(empty)}건")
    chars = [len(d.text) for d in docs]
    if chars:
        print(f"  - 문서 글자 수: 중앙값 {statistics.median(chars):,.0f}, 최소 {min(chars):,}, 최대 {max(chars):,}")
    lens = [len(c.text) for c in chunks]
    print(
        f"[청크] {len(chunks):,}개 (chunk_size={chk['chunk_size']}, overlap={chk['chunk_overlap']},"
        f" header={chk.get('add_header', True)})"
    )
    if lens:
        qs = statistics.quantiles(lens, n=20)
        per_doc = Counter(c.doc_id for c in chunks)
        print(
            f"  - 청크 길이: 평균 {statistics.mean(lens):.0f}, 중앙값 {statistics.median(lens):.0f},"
            f" p5 {qs[0]:.0f}, p95 {qs[-1]:.0f}, 최소 {min(lens)}, 최대 {max(lens)}"
        )
        print(
            f"  - 100자 미만 청크 {sum(1 for n in lens if n < 100)}개,"
            f" 문서당 청크 중앙값 {statistics.median(per_doc.values()):.0f} (최대 {max(per_doc.values())})"
        )
        with_page = sum(1 for c in chunks if "page" in c.metadata)
        print(f"  - 페이지 정보가 있는 청크: {with_page}개 (PDF)")


if __name__ == "__main__":
    main()
