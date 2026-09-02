"""Real-behavior test for _guidance_query() — hits the actual meridian
retriever, not a fake. FakeRetriever returns the same canned chunks
regardless of query text, so it can never catch a query that's well-formed
Python but retrieves nothing from the real corpus.

Per test-behavior-real.md: every spec needs at least one test that
exercises real behavior against a real client. Costs real retrieval work,
so it never runs by default — see gatople_api/pyproject.toml's addopts
(`-m "not eval"`).

Run explicitly:
    cd gatople_api && uv run pytest -m eval
"""

from __future__ import annotations

import pytest

from gatople_api.bootstrap import build_services
from gatople_api.routes.generate import GenerateBody, _guidance_query

pytestmark = pytest.mark.eval


@pytest.mark.parametrize("flavor", ["free", "penta-walk", "carta-progression"])
async def test_guidance_query_retrieves_real_book_content(flavor: str) -> None:
    # Caught live on :5174: the prior _guidance_query() mixed meta-language
    # about "Strudel"/"live coding" (concepts the book never discusses)
    # with raw numeric role/glyph noise, and reliably retrieved ZERO real
    # chunks for every flavor — every single Strudel generation silently
    # fell back to StubExpert's generic quote regardless of what was
    # actually generated. A FakeRetriever-backed test can't catch this: it
    # returns the same canned chunks no matter what query text is sent.
    services = build_services()
    body = GenerateBody(tonic="A", mode="Eólico", length=16, flavor=flavor)
    query = _guidance_query(body=body)

    chunks = await services.retriever.search(question=query, k=8)

    assert chunks, f"flavor={flavor!r} retrieved zero real chunks for query: {query!r}"
