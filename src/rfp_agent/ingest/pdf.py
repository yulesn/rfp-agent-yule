"""PDF 파서 (PyMuPDF).

- 역할: PDF 한 개를 페이지별 텍스트로 추출한다. 표는 `page.find_tables()` 로 찾아 마크다운으로 바꿔 문서 위치에 넣는다.
- 계약: parse_pdf(path) -> RfpDocument (pages 채움, file_type="pdf", text = 페이지 텍스트를 이은 전체).
- 소속: Phase 1 (플랜 3절 5번). 표 많은 문서는 Phase 5에서 pymupdf4llm/Docling 비교.

표 처리: 행/열이 2 이상인 표만 표로 보고(한 칸짜리는 오탐이 많다), 표 영역과 겹치는 텍스트 블록은 빼고
표 마크다운을 표의 세로 위치에 끼워 넣는다. 다단 레이아웃에서는 읽기 순서가 틀릴 수 있다(알려진 한계).
"""

from pathlib import Path
from typing import Any

from rfp_agent.ingest.naming import make_doc_id, normalize_name
from rfp_agent.ingest.schema import PageText, RfpDocument


def _cell(value: Any) -> str:
    """셀 값을 한 줄 문자열로 만든다 (줄바꿈은 공백, 파이프는 이스케이프)."""
    return " ".join(str(value or "").split()).replace("|", "\\|")


def _table_markdown(table: Any) -> str:
    """표를 마크다운으로 바꾼다. 완전히 빈 행/열은 버리고 첫 행을 머리글로 쓴다.

    pymupdf 의 to_markdown 은 병합 셀 때문에 생긴 빈 열에 `Col2` 같은 이름을 붙이므로 직접 만든다.
    """
    rows = [[_cell(c) for c in row] for row in (table.extract() or [])]
    rows = [r for r in rows if any(r)]
    if not rows:
        return ""
    keep = [i for i in range(max(len(r) for r in rows)) if any(i < len(r) and r[i] for r in rows)]
    rows = [[r[i] if i < len(r) else "" for i in keep] for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join("---" for _ in keep) + " |"]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def _inside(block: tuple[float, ...], bbox: tuple[float, ...]) -> bool:
    """블록 중심이 표 영역 안에 있으면 True."""
    cx, cy = (block[0] + block[2]) / 2, (block[1] + block[3]) / 2
    return bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]


def page_to_text(page: Any) -> str:
    """한 페이지를 텍스트로 만든다 (표는 마크다운으로 위치에 삽입)."""
    try:
        tables = [t for t in page.find_tables().tables if t.row_count >= 2 and t.col_count >= 2]
    except Exception:  # noqa: BLE001 - 표 탐지 실패 시 일반 텍스트로
        tables = []
    if not tables:
        return page.get_text("text", sort=True).strip()

    items: list[tuple[float, float, str]] = []  # (y0, x0, text)
    for block in page.get_text("blocks", sort=True):
        if block[6] != 0:  # 이미지 블록 제외
            continue
        if any(_inside(block, t.bbox) for t in tables):
            continue
        text = block[4].strip()
        if text:
            items.append((block[1], block[0], text))
    for t in tables:
        md = _table_markdown(t)
        if md:
            items.append((t.bbox[1], t.bbox[0], md))
    items.sort(key=lambda it: (round(it[0], 1), it[1]))
    return "\n\n".join(it[2] for it in items)


def parse_pdf(path: str | Path) -> RfpDocument:
    """PDF 를 RfpDocument 로 변환한다."""
    import pymupdf

    pymupdf.TOOLS.mupdf_display_errors(False)  # 참조되지 않는 깨진 객체 경고 등 소음 제거 (무해, docs/trials)
    path = Path(path)
    pages: list[PageText] = []
    with pymupdf.open(path) as doc:
        for i, page in enumerate(doc, start=1):
            pages.append(PageText(page=i, text=page_to_text(page)))
    return RfpDocument(
        doc_id=make_doc_id(path.name),
        file_name=normalize_name(path.name),
        file_type="pdf",
        text="\n\n".join(p.text for p in pages if p.text),
        pages=pages,
    )
