"""스모크 테스트: 모든 모듈이 import 되고 설정/스키마가 동작하는지 확인한다."""

import importlib

import pytest

from rfp_agent.config import load_config
from rfp_agent.ingest.schema import Chunk, PageText, RfpDocument

MODULES = [
    "rfp_agent",
    "rfp_agent.config",
    "rfp_agent.llm",
    "rfp_agent.ingest.schema",
    "rfp_agent.ingest.pdf",
    "rfp_agent.ingest.hwp",
    "rfp_agent.ingest.metadata",
    "rfp_agent.ingest.loader",
    "rfp_agent.ingest.chunking",
    "rfp_agent.retrieval.embeddings",
    "rfp_agent.retrieval.vectorstore",
    "rfp_agent.retrieval.retriever",
    "rfp_agent.retrieval.metadata_filter",
    "rfp_agent.agent.state",
    "rfp_agent.agent.prompts",
    "rfp_agent.agent.nodes",
    "rfp_agent.agent.graph",
    "rfp_agent.agent.tools",
    "rfp_agent.agent.tools.search_rfp",
    "rfp_agent.agent.tools.filter_rfps",
    "rfp_agent.evaluation.metrics",
    "rfp_agent.evaluation.judge",
]


@pytest.mark.parametrize("name", MODULES)
def test_import(name: str) -> None:
    importlib.import_module(name)


def test_load_config() -> None:
    config = load_config("configs/default.yaml")
    assert config["chunking"]["chunk_size"] == 1000
    assert config["embedding"]["model"] == "BAAI/bge-m3"
    assert config["paths"]["raw_dir"].endswith("data/raw")


def test_schema_models() -> None:
    page = PageText(page=1, text="안녕")
    doc = RfpDocument(
        doc_id="a", file_name="a.pdf", file_type="pdf", text="안녕", pages=[page]
    )
    assert doc.metadata == {}
    chunk = Chunk(chunk_id="a-0", doc_id=doc.doc_id, text="안녕")
    assert chunk.metadata == {}


def test_tools_registered() -> None:
    from rfp_agent.agent.tools import ALL_TOOLS

    assert {t.name for t in ALL_TOOLS} == {"search_rfp", "filter_rfps"}
