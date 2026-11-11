"""PDF 파서 테스트: 합성 PDF 로 페이지 채움과 표 마크다운 변환을 확인한다 (실제 문서 없음)."""

from pathlib import Path

import pymupdf

from rfp_agent.ingest.pdf import parse_pdf


def _make_pdf(path: Path, with_table: bool) -> None:
    doc = pymupdf.open()
    p1 = doc.new_page()
    p1.insert_text((72, 100), "First page text alpha", fontsize=12)
    p2 = doc.new_page()
    p2.insert_text((72, 80), "Second page intro", fontsize=12)
    if with_table:
        x0, y0, cw, rh = 72, 120, 120, 28
        for r in range(4):  # 3행 x 3열 격자
            p2.draw_line((x0, y0 + r * rh), (x0 + 3 * cw, y0 + r * rh))
        for c in range(4):
            p2.draw_line((x0 + c * cw, y0), (x0 + c * cw, y0 + 3 * rh))
        cells = [["Item", "Cost", "Note"], ["Dev", "1000", "a"], ["Ops", "2000", "b"]]
        for r, row in enumerate(cells):
            for c, text in enumerate(row):
                p2.insert_text((x0 + c * cw + 6, y0 + r * rh + 18), text, fontsize=11)
        p2.insert_text((72, 300), "After table text", fontsize=12)
    doc.save(path)
    doc.close()


def test_parse_pdf_pages(tmp_path: Path) -> None:
    f = tmp_path / "sample.pdf"
    _make_pdf(f, with_table=False)
    doc = parse_pdf(f)
    assert doc.file_type == "pdf" and doc.doc_id == "sample"
    assert doc.pages is not None and [p.page for p in doc.pages] == [1, 2]
    assert "First page text alpha" in doc.pages[0].text
    assert "First page text alpha" in doc.text and "Second page intro" in doc.text


def test_parse_pdf_table_as_markdown(tmp_path: Path) -> None:
    f = tmp_path / "table.pdf"
    _make_pdf(f, with_table=True)
    doc = parse_pdf(f)
    assert doc.pages is not None
    text = doc.pages[1].text
    assert "| Item | Cost | Note |\n| --- | --- | --- |\n| Dev | 1000 | a |\n| Ops | 2000 | b |" in text
    assert "Col" not in text  # 빈 열에 임의 이름이 붙지 않음
    # 표 앞뒤 일반 텍스트 순서 유지
    assert text.index("Second page intro") < text.index("Item") < text.index("After table text")
