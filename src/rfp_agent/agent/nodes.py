"""그래프 노드 함수.

- 역할: 그래프의 각 노드(LLM 호출, 도구 실행 등) 구현.
- 계약: 노드는 AgentState 를 받아 상태 업데이트 dict 를 반환한다.
- 소속: Phase 1 은 agent 노드 하나. Phase 3 에서 router/근거 검증 노드 추가.
"""

from typing import Any

from rfp_agent.agent.state import AgentState


def agent_node(state: AgentState, config: dict[str, Any]) -> dict[str, Any]:
    """LLM(도구 바인딩)을 호출하고 응답 메시지를 상태에 추가한다."""
    # TODO: get_llm(config).bind_tools(ALL_TOOLS) 에 SYSTEM_PROMPT + messages 를 넣어 호출
    raise NotImplementedError
