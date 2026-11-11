"""데이터 탐색 스크립트.

- 역할: data/raw 의 파일 형식 비율, 페이지 수, 스캔 PDF 여부, 메타데이터 컬럼을 요약한다.
- 사용: uv run python scripts/inspect_data.py --config configs/default.yaml
- 소속: Phase 1 (플랜 2절 Phase 1-1).
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="RFP 데이터 탐색")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.parse_args()
    # TODO: 확장자별 개수, PDF 페이지 수, 텍스트 거의 없는 PDF(스캔 의심) 비율, CSV 컬럼 출력
    raise NotImplementedError


if __name__ == "__main__":
    main()
