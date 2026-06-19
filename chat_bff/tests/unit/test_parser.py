"""Citation parser tests — pure-string in, structured out."""

from chat_bff.citations.parser import CITATION_RE, parse_answer


def test_parses_canonical_form() -> None:
    text = "El Dodecamundo es doce mundos [b202598c·ch0§0¶27 p.16]."
    claims = parse_answer(text)
    assert len(claims) == 1
    assert claims[0].sentence == "El Dodecamundo es doce mundos ."
    assert len(claims[0].citations) == 1
    cite = claims[0].citations[0]
    assert cite.book_hash == "b202598c"
    assert cite.chapter_idx == 0
    assert cite.paragraph_idx == 27
    assert cite.page_start == 16


def test_parses_ascii_fallback_form() -> None:
    """The LLM drifts to ASCII separators sometimes; parser tolerates it."""
    text = "Frigio is dominant of Eólico [b202598c.ch0.0.45 p.26]."
    claims = parse_answer(text)
    assert len(claims[0].citations) == 1
    assert claims[0].citations[0].book_hash == "b202598c"
    assert claims[0].citations[0].paragraph_idx == 45


def test_multiple_sentences_each_get_their_citations() -> None:
    text = (
        "First claim [f39cb7c5·ch0§0¶3 p.4]. "
        "Second claim [b202598c·ch0§0¶17 p.11]."
    )
    claims = parse_answer(text)
    assert len(claims) == 2
    assert claims[0].citations[0].book_hash == "f39cb7c5"
    assert claims[1].citations[0].book_hash == "b202598c"


def test_uncited_sentence_returns_empty_citations() -> None:
    text = "This claim has no citation."
    claims = parse_answer(text)
    assert len(claims) == 1
    assert claims[0].citations == ()


def test_two_citations_on_one_sentence() -> None:
    text = "Compound claim [f39cb7c5·ch0§0¶3 p.4][b202598c·ch0§0¶17 p.11]."
    claims = parse_answer(text)
    assert len(claims) == 1
    assert len(claims[0].citations) == 2


def test_malformed_citation_is_ignored() -> None:
    """Wrong number of digits in book_hash → no match, not a parse error."""
    text = "Bad cite [zzzz·ch0§0¶1 p.1]."
    claims = parse_answer(text)
    assert claims[0].citations == ()


def test_question_mark_ends_a_sentence() -> None:
    text = "What is Eólico? [b202598c·ch0§0¶17 p.11]."
    claims = parse_answer(text)
    assert len(claims) == 2  # the question + the trailing fragment
    # The citation belongs to whichever fragment contains it
    citing = [c for c in claims if c.citations]
    assert len(citing) == 1


def test_bare_regex_matches_extra_whitespace() -> None:
    """Direct regex check — the parser layer trims, but the regex itself
    must accept lazy whitespace."""
    assert CITATION_RE.search("[f39cb7c5 ch0  §0 ¶3   p. 4]") is not None
