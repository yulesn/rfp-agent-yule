"""청킹.

- 역할: RfpDocument 를 검색 단위 Chunk 로 나눈다.
- 계약: chunk_document(doc, chunk_size, chunk_overlap) -> list[Chunk]
  각 Chunk.metadata 에 doc_id, page(가능하면), 문서 메타를 담아 출처 인용에 쓴다.
- 소속: Phase 1 = 고정 길이 재귀 분할(langchain-text-splitters).
  Phase 5 에서 구조 기반(목차/조항), parent-child, 표 마크다운 통째로 실험.
  아이디어: 청크 앞에 문서 메타 헤더(사업명/기관)를 붙여 검색 품질을 올린다.
"""

from rfp_agent.ingest.schema import Chunk, RfpDocument


def chunk_document(doc: RfpDocument, chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    """문서를 고정 길이로 나눠 Chunk 리스트를 만든다."""
    # TODO: RecursiveCharacterTextSplitter (lazy import), 페이지가 있으면 페이지별로 분할
    raise NotImplementedError
