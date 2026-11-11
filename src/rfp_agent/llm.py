"""LLM 팩토리.

- 역할: 설정(config["llm"])만 보고 채팅 모델을 만든다. 모델 교체는 설정 파일만 바꾸면 된다.
- 계약: get_llm(config) -> BaseChatModel
- 소속: Phase 1 (플랜 3절 3번, LLM 호출 방식).
"""

from typing import Any


def get_llm(config: dict[str, Any]):
    """config["llm"] 의 provider/model/temperature 로 채팅 모델을 만든다."""
    from langchain.chat_models import init_chat_model

    llm_cfg = config["llm"]
    return init_chat_model(
        model=llm_cfg["model"],
        model_provider=llm_cfg["provider"],
        temperature=llm_cfg.get("temperature", 0),
    )
