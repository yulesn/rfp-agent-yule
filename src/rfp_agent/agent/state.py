"""에이전트 상태.

- 역할: 그래프 노드들이 공유하는 상태 정의.
- 계약: AgentState.messages 는 add_messages reducer 로 누적된다.
- 소속: Phase 1. Phase 3 에서 라우팅 결과, 근거 검증 플래그 등을 추가.
"""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """대화 메시지만 담는 최소 상태."""

    messages: Annotated[list, add_messages]
