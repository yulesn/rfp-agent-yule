"""청킹 테스트 (합성 문서)."""

from rfp_agent.ingest.chunking import chunk_document, split_text
from rfp_agent.ingest.schema import PageText, RfpDocument

META = {"title": "테스트 사업", "agency": "테스트 기관", "amount": 1000, "bid_end": "2024-10-15T17:00:00", "summary": "x"}


def _doc(**kw) -> RfpDocument:  # type: ignore[no-untyped-def]
    base = {"doc_id": "d1", "file_name": "d1.hwp", "file_type": "hwp", "text": "", "metadata": META}
    base.update(kw)
    return RfpDocument(**base)


def test_header_and_metadata() -> None:
    doc = _doc(text="가나다라 " * 100)
    chunks = chunk_document(doc, 100, 10)
    assert len(chunks) > 1
    first = chunks[0]
    assert first.text.startswith("[테스트 사업 | 테스트 기관]\n")
    assert first.chunk_id == "d1-0000" and chunks[1].chunk_id == "d1-0001"
    assert first.metadata["doc_id"] == "d1"
    assert first.metadata["title"] == "테스트 사업" and first.metadata["amount"] == 1000
    assert first.metadata["bid_end"] == "2024-10-15T17:00:00"
    assert "summary" not in first.metadata  # 키는 선별해서 담는다
    assert "page" not in first.metadata  # HWP 는 페이지 없음


def test_header_off_and_missing_metadata() -> None:
    doc = _doc(text="본문 " * 50, metadata={"title": "T", "amount": None})
    chunks = chunk_document(doc, 100, 0, add_header=False)
    assert not chunks[0].text.startswith("[")
    assert "amount" not in chunks[0].metadata  # None 은 뺀다 (Chroma 호환)


def test_pdf_pages_keep_page_number() -> None:
    doc = _doc(
        file_type="pdf",
        pages=[PageText(page=1, text="첫 쪽 " * 30), PageText(page=2, text=""), PageText(page=3, text="셋째 쪽")],
    )
    chunks = chunk_document(doc, 1000, 0)
    assert [c.metadata["page"] for c in chunks] == [1, 3]
    assert [c.metadata["chunk_index"] for c in chunks] == [0, 1]


def test_table_kept_whole_when_it_fits() -> None:
    table = "| 항목 | 금액 |\n| --- | --- |\n| 개발비 | 1,000 |\n| 운영비 | 2,000 |"
    text = ("앞 문단 " * 40) + "\n\n" + table + "\n\n" + ("뒤 문단 " * 40)
    pieces = split_text(text, 300, 0)
    holders = [p for p in pieces if "| 개발비 |" in p]
    assert len(holders) == 1 and table in holders[0]  # 표가 쪼개지지 않음


def test_big_table_split_by_rows_with_header_repeated() -> None:
    rows = "\n".join(f"| 행{i} | {i * 100} |" for i in range(60))
    table = "| 항목 | 값 |\n| --- | --- |\n" + rows
    pieces = split_text(table, 200, 0)
    assert len(pieces) > 1
    assert all(p.startswith("| 항목 | 값 |\n| --- | --- |") for p in pieces)
    assert all(len(p) <= 260 for p in pieces)
    joined = "\n".join(pieces)
    assert "| 행0 |" in joined and "| 행59 |" in joined  # 행 누락 없음


def test_empty_document() -> None:
    assert chunk_document(_doc(text="  \n "), 100, 10) == []


def test_oversize_row_is_split_and_bounded() -> None:
    long_cell = "요구사항 " * 300  # 한 행이 chunk_size 보다 훨씬 김
    table = f"| 항목 | 내용 |\n| --- | --- |\n| 기능 | {long_cell} |\n| 끝 | 마지막 |"
    pieces = split_text(table, 300, 0)
    assert len(pieces) > 3
    assert all(len(p) <= 330 for p in pieces)  # 헤더 포함해도 상한 근처
    assert any("| 끝 | 마지막 |" in p for p in pieces)
