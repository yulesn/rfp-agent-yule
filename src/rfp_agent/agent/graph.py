"""그래프 조립.

- 역할: StateGraph 를 만들어 컴파일한다.
- 계약: build_graph(config) -> 컴파일된 그래프 (invoke({"messages": [...]}) 지원)
- 소속: Phase 1 / Phase 3.

Phase 1 베이스라인:
    START -> agent <-> tools -> END
    (agent 가 tool_calls 를 내면 tools 로, 아니면 END)

Phase 3 목표:
    START -> router -> (범위 밖 응답 | 단순 메타 조회 | RAG 에이전트 루프) -> 근거 검증 -> 응답
"""

from typing import Any


def build_graph(config: dict[str, Any]):
    """에이전트 그래프를 만든다."""
    # TODO: llm = get_llm(config); vectorstore/metadata_df 로드 후 tools = build_tools(...);
    #       agent 노드 = make_agent_node(llm.bind_tools(tools)); ToolNode(tools) 와
    #       tools_condition 조건부 엣지로 StateGraph(AgentState) 조립
    raise NotImplementedError
