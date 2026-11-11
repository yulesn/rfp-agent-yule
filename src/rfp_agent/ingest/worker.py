"""파일 1개를 파싱해 JSON 으로 저장하는 워커 (별도 프로세스에서 실행).

- 사용: python -m rfp_agent.ingest.worker <문서 경로> <출력 JSON 경로>
- 역할: 외부 파서가 멈추거나 죽어도 배치 전체가 영향받지 않게 파일마다 프로세스를 분리한다 (ADR 0005).
- 결과는 stdout 이 아니라 파일로 쓴다 (파서/라이브러리가 stdout 에 무엇을 찍어도 결과가 섞이지 않게).
"""

import sys
from pathlib import Path

from rfp_agent.ingest.loader import load_document


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python -m rfp_agent.ingest.worker <path> <out_json>", file=sys.stderr)
        return 2
    doc = load_document(argv[0])
    Path(argv[1]).write_text(doc.model_dump_json(), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
