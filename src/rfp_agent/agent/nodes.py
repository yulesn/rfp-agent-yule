"""그래프 노드 함수.

- 역할: 그래프의 각 노드(LLM 호출 등) 구현.
- 계약: make_agent_node(llm_with_tools) -> 노드 함수 (state: AgentState) -> dict.
  노드는 상태 업데이트 dict 를 반환한다. LLM 은 외부에서 만들어 주입한다(전역 상태 없음).
- 소속: Phase 1 은 agent 노드 하나. Phase 3 에서 router/근거 검증 노드 추가.
"""

from collections.abc import Callable
from typing import Any

from rfp_agent.agent.state import AgentState


def make_agent_node(llm_with_tools) -> Callable[[AgentState], dict[str, Any]]:
    """도구가 바인딩된 LLM 으로 agent 노드 함수를 만든다."""

    def agent_node(state: AgentState) -> dict[str, Any]:
        # TODO: [SystemMessage(SYSTEM_PROMPT), *state["messages"]] 로 llm_with_tools.invoke
        raise NotImplementedError

    return agent_node
