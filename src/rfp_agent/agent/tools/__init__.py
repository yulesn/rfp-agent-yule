"""에이전트 도구 모음 (1파일 1도구).

- 계약: build_tools(vectorstore, metadata_df) -> list[BaseTool]. 의존성(벡터스토어, 메타데이터)은
  클로저로 주입하며 모듈 전역 상태는 쓰지 않는다. 반환된 도구가 에이전트에 바인딩된다.
- 소속: Phase 1 (도구 2개), Phase 3 에서 확장.
"""

import pandas as pd
from langchain_core.tools import BaseTool

from rfp_agent.agent.tools.filter_rfps import make_filter_rfps_tool
from rfp_agent.agent.tools.search_rfp import make_search_rfp_tool


def build_tools(vectorstore, metadata_df: pd.DataFrame) -> list[BaseTool]:
    """검색/필터 도구를 만들어 리스트로 반환한다."""
    return [make_search_rfp_tool(vectorstore), make_filter_rfps_tool(metadata_df)]
