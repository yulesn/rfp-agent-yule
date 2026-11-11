"""인덱스 구축 CLI.

- 역할: 파싱 -> data/processed/*.jsonl 저장 -> 청킹 -> 임베딩 -> Chroma 적재.
- 사용: uv run python scripts/build_index.py --config configs/default.yaml
- 소속: Phase 1.
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="RFP 인덱스 구축")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.parse_args()
    # TODO: load_config -> load_metadata -> load_all -> chunk_document -> add_chunks
    raise NotImplementedError


if __name__ == "__main__":
    main()
