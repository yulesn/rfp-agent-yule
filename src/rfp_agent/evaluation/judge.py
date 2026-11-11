"""LLM-as-a-judge.

- 역할: 답변의 정답성, 근거 충실도, 인용 정확도를 채점한다.
- 계약: judge_answer(question, reference, answer, config) -> dict (항목별 점수와 사유)
  judge 모델(config["judge"])은 답변 모델과 다른 계열이어야 한다(자기 편향 방지).
- 소속: Phase 2. 사람 채점 20건과 일치율을 확인한다.
"""

from typing import Any


def judge_answer(
    question: str, reference: str, answer: str, config: dict[str, Any]
) -> dict[str, Any]:
    """judge 모델로 답변을 채점한다."""
    # TODO: structured output 으로 항목별 점수 반환
    raise NotImplementedError
