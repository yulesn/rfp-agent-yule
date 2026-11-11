"""Chroma 벡터스토어.

- 역할: 로컬 파일 기반 Chroma 를 열고 청크를 적재한다.
- 계약:
  - get_vectorstore(config, embeddings) -> langchain_chroma.Chroma
    (persist_directory = config["paths"]["vectorstore_dir"], collection = config["vectorstore"])
  - add_chunks(store, chunks) -> None
- 소속: Phase 1, ADR 0003 (Chroma 만 사용).
"""

from typing import Any

from rfp_agent.ingest.schema import Chunk


def get_vectorstore(config: dict[str, Any], embeddings):
    """설정의 경로/컬렉션 이름으로 Chroma 를 연다."""
    # TODO: langchain_chroma.Chroma (lazy import)
    raise NotImplementedError


def add_chunks(store, chunks: list[Chunk]) -> None:
    """청크를 배치로 Chroma 에 넣는다. chunk_id 를 id 로 써서 재실행 시 중복을 막는다."""
    # TODO: store.add_texts(texts, metadatas, ids) 를 배치로 호출
    raise NotImplementedError
