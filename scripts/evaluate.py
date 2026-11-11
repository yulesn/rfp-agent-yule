"""평가 실행 CLI.

- 역할: eval/questions.v*.jsonl 로 검색/답변 지표를 계산하고 결과 표와 실패 사례를 저장한다.
- 사용: uv run python scripts/evaluate.py --config configs/default.yaml
- 소속: Phase 2.
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="평가셋 실행")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--questions", default="eval/questions.v1.jsonl")
    parser.parse_args()
    # TODO: 질문별 에이전트 실행(캐시), hit_at_k/mrr/judge 계산, 결과 저장
    raise NotImplementedError


if __name__ == "__main__":
    main()
