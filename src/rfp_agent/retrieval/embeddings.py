"""임베딩 모델 팩토리.

- 역할: 설정으로 임베딩 모델을 만든다. 기본은 로컬 HuggingFace (BAAI/bge-m3, 무료).
- 계약: get_embeddings(config) -> langchain Embeddings (config["embedding"] 사용)
- 소속: Phase 1 (플랜 3절 6번). 모델 비교는 Phase 6.
"""

from typing import Any


def get_embeddings(config: dict[str, Any]):
    """config["embedding"] 로 임베딩 객체를 만든다."""
    # TODO: langchain_huggingface.HuggingFaceEmbeddings (lazy import), device 는 설정값
    raise NotImplementedError
