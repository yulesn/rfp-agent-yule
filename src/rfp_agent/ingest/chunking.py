"""청킹.

- 역할: RfpDocument 를 검색 단위 Chunk 로 나눈다.
- 계약: chunk_document(doc, chunk_size, chunk_overlap, add_header=True) -> list[Chunk]
  - chunk_id = "{doc_id}-{순번:04d}". 각 Chunk.metadata 에 doc_id, chunk_index, file_name/file_type,
    page(PDF 만), 그리고 문서 메타 중 title, agency, amount, bid_end 를 담는다 (값이 없는 키는 뺀다. Chroma 는 None 불가).
  - add_header=True 면 청크 본문 앞에 "[사업명 | 발주기관]" 한 줄을 붙인다. chunk_size 는 헤더를 뺀 본문 길이 기준이다.
- 소속: Phase 1 = 고정 길이 재귀 분할(langchain-text-splitters). Phase 5 에서 구조 기반/parent-child 등 실험.

표 처리: 마크다운 표(연속된 `|` 줄)는 가능하면 쪼개지 않고 통째로 한 덩어리로 다룬다. 한 표가 chunk_size 를 넘으면
행 단위로 나누고 매 조각에 헤더 행(첫 두 줄)을 반복한다(행 하나가 더 길면 글자 단위로 쪼갠다). 텍스트 구간과 표 구간 사이에는 겹침(overlap)이 없다.
PDF 는 페이지별로 나누므로 페이지에 걸친 표는 잘린다 (알려진 한계).
"""

import re
from typing import Any

from rfp_agent.ingest.schema import Chunk, RfpDocument

_TABLE_LINE = re.compile(r"^\s*\|.*\|\s*$")
META_KEYS = ("title", "agency", "amount", "bid_end")


def _split_blocks(text: str) -> list[tuple[bool, str]]:
    """텍스트를 (is_table, 내용) 덩어리로 나눈다. 연속된 마크다운 표 줄이 표 덩어리다."""
    blocks: list[tuple[bool, str]] = []
    buf: list[str] = []
    in_table = False
    for line in text.split("\n"):
        is_row = bool(_TABLE_LINE.match(line))
        if is_row != in_table and buf:
            blocks.append((in_table, "\n".join(buf)))
            buf = []
        in_table = is_row
        buf.append(line)
    if buf:
        blocks.append((in_table, "\n".join(buf)))
    return [(t, s) for t, s in blocks if s.strip()]


def _split_table(table: str, chunk_size: int, chunk_overlap: int = 0) -> list[str]:
    """chunk_size 를 넘는 표를 행 단위로 나누고 헤더 행(첫 두 줄)을 반복한다.

    한 행(셀 안에 긴 본문이 든 경우)이 혼자 chunk_size 를 넘으면 그 행의 글자를 재귀 분할기로 쪼개고,
    조각마다 헤더를 붙인다 (표 문법은 깨지지만 길이 상한은 지킨다).
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    lines = table.split("\n")
    head_text = "\n".join(lines[:2])
    body = lines[2:]
    if len(head_text) > chunk_size // 2:  # 헤더가 너무 길면 반복하지 않는다
        head_text, body = "", lines
    prefix = head_text + "\n" if head_text else ""
    room = max(chunk_size - len(prefix), chunk_size // 2)
    row_splitter = RecursiveCharacterTextSplitter(chunk_size=room, chunk_overlap=chunk_overlap)

    pieces: list[str] = []
    cur: list[str] = []
    cur_len = len(prefix)

    def flush() -> None:
        nonlocal cur, cur_len
        if cur:
            pieces.append(prefix + "\n".join(cur))
        cur, cur_len = [], len(prefix)

    for row in body:
        if len(row) > room:  # 긴 행은 따로 쪼갠다
            flush()
            pieces.extend(prefix + part for part in row_splitter.split_text(row))
            continue
        if cur and cur_len + len(row) + 1 > chunk_size:
            flush()
        cur.append(row)
        cur_len += len(row) + 1
    flush()
    return pieces or [head_text]


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """표는 통째로, 나머지는 재귀 분할로 나눈 뒤 chunk_size 안에서 이웃 조각을 이어 붙인다."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    pieces: list[str] = []
    for is_table, block in _split_blocks(text):
        if not is_table:
            pieces.extend(splitter.split_text(block))
        elif len(block) <= chunk_size:
            pieces.append(block)
        else:
            pieces.extend(_split_table(block, chunk_size, chunk_overlap))

    packed: list[str] = []
    cur = ""
    for piece in pieces:
        if cur and len(cur) + 2 + len(piece) <= chunk_size:
            cur = f"{cur}\n\n{piece}"
        else:
            if cur:
                packed.append(cur)
            cur = piece
    if cur:
        packed.append(cur)
    return [p for p in packed if p.strip()]


def _header(meta: dict[str, Any]) -> str:
    title, agency = meta.get("title"), meta.get("agency")
    parts = [p for p in (title, agency) if p]
    return f"[{' | '.join(parts)}]" if parts else ""


def chunk_document(
    doc: RfpDocument, chunk_size: int, chunk_overlap: int, add_header: bool = True
) -> list[Chunk]:
    """문서를 나눠 Chunk 리스트를 만든다. PDF 는 페이지별, 그 외는 문서 전체를 대상으로 한다."""
    base: dict[str, Any] = {
        "doc_id": doc.doc_id,
        "file_name": doc.file_name,
        "file_type": doc.file_type,
    }
    for key in META_KEYS:
        value = doc.metadata.get(key)
        if value is not None:
            base[key] = value
    header = _header(doc.metadata) if add_header else ""

    segments: list[tuple[int | None, str]]
    if doc.pages:
        segments = [(p.page, p.text) for p in doc.pages if p.text.strip()]
    else:
        segments = [(None, doc.text)]

    chunks: list[Chunk] = []
    for page, text in segments:
        for piece in split_text(text, chunk_size, chunk_overlap):
            idx = len(chunks)
            meta = {**base, "chunk_index": idx}
            if page is not None:
                meta["page"] = page
            body = f"{header}\n{piece}" if header else piece
            chunks.append(Chunk(chunk_id=f"{doc.doc_id}-{idx:04d}", doc_id=doc.doc_id, text=body, metadata=meta))
    return chunks
