"""질의응답 CLI.

- 역할: 질문 하나를 에이전트에 보내고 출처가 달린 답변을 출력한다.
- 사용: uv run python scripts/ask.py "질문" --config configs/default.yaml
- 소속: Phase 1.
"""

import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="RFP 에이전트에게 질문하기")
    parser.add_argument("question")
    parser.add_argument("--config", default="configs/default.yaml")
    parser.parse_args()
    # TODO: build_graph(config).invoke({"messages": [("user", question)]}) 후 마지막 메시지 출력
    raise NotImplementedError


if __name__ == "__main__":
    main()
