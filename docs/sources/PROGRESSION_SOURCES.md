# Progression Sources

Each progression in `docs/gatople/progressions.json` carries a `book_ref` field.
This file documents what those refs mean and how to verify them.

## Source corpus

The progressions are sourced from two of Patricio Torres's books:

| Short ref | Title | Indexed at `~/.meridian/library` |
|---|---|---|
| `fractal_libro` | *El Sistema Fractal* (Torres, 2024) — full text | `b202598c` (Chapter 0 only — published in this repo's index) |
| `disonancia` | *El Lujo de la Disonancia* — DodecaFuga material | (not yet indexed) |

The second indexed book, `f39cb7c5` (*2025 Fractal Music World*), is the
shorter summary book and does not host the cadence-by-cadence pedagogy
that the progressions cite.

## Ref format

`<source>:<line-number>` — the line number is into the plaintext export of
the book, not the published PDF. Two reasons we keep this shape:

1. The plaintext export is what the deep-ingest pass read from. Line numbers
   stay stable across re-builds of the index.
2. We don't have published page numbers we trust for either book — Torres's
   PDFs are layout-dense and pagination shifts between editions.

## How to verify a ref

Until `disonancia` and the full *Sistema Fractal* are indexed under
`~/.meridian/library`, the most reliable verification is to search the
indexed corpus for the *substance* of the claim:

```bash
cd iccha_context_multi_agent/meridian_library
uv run meridian-library search "Función Cíclica volvemos" \
  --index-dir ~/.meridian/library --hybrid \
  --book b202598c --book f39cb7c5
```

**2026-09-01 correction.** This section previously claimed `matriarchal-cycle`
and `flamenco-opener` had "already done this round-trip" with the indexed
passage matching their `summary` field verbatim, citing
`[b202598c] ch0 §0 ¶17 p.11` and a full-book match for a Flamenco quote.
Re-ran the exact command above (plus direct searches for `"Función
Cíclica"`, `"CERO Alteraciones"`, and `"Flamenco"` individually) and found
neither exists anywhere in the indexed corpus — `¶17 p.11` is a real chunk,
but its actual text is about La menor producing the major tonality, not
about "función cíclica"; "Flamenco" doesn't appear in either indexed book
at all. **That earlier "verified" claim was wrong — it reported a failed
verification as a successful one.**

The likely explanation, not a claim that the underlying content is
invented: `progressions.json`'s real `book_ref` for both of these is
`fractal_libro:1045` / `fractal_libro:1424` — line numbers into the book's
full plaintext export, a completely different addressing scheme from
meridian's chunk index (`chN §M ¶P pQ`). Only Chapter 0 of `b202598c` is
currently indexed in meridian; lines 1045/1424 may simply fall outside
that indexed range, in which case the content could be entirely real and
this doc's attempted cross-reference into the chunk index was just the
wrong tool for verifying it. Either way, **these two book_refs are
unverified against the current index** — not confirmed, not disproven.
Do not cite the removed chunk references as if they were checked; treat
`matriarchal-cycle` and `flamenco-opener` the same as every other
`fractal_libro:*` reference below until the full book is indexed.

The remaining references (`disonancia:*` and the deeper `fractal_libro:*`
lines) describe content that is in the books but not in the published
index here. We're keeping the refs as honest pointers; once the full
books are indexed they will become directly resolvable.

## Resolving a ref to a meridian chunk

When the full books land in the index, the build script will be updated
to translate every `book_ref` into a structured chunk address. The shape
below is illustrative only — the numbers are a schema example, not a
verified address for any specific progression (they happen to reuse
`¶17 p.11`, the same chunk the correction above found does *not* contain
what was once claimed for it):

```json
{
  "book_ref": [
    {
      "book_hash": "b202598c",
      "chapter_idx": 0,
      "section_idx": 0,
      "paragraph_idx": 17,
      "page_start": 11
    }
  ]
}
```

The current flat string form is the interim shape. Consumers should
treat `book_ref` as opaque and route verification through this document.
