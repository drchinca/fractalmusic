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

For two cadences we have already done this round-trip and the indexed
passage matches the `summary` field of the JSON entry verbatim:

| Progression | Indexed match |
|---|---|
| `matriarchal-cycle` | `[b202598c]` ch0 §0 ¶17 p.11 — *"Función Cíclica … volvemos a la tonalidad … con CERO Alteraciones"* |
| `flamenco-opener` | full-book text match for *"Es la base sonora de la música Árabe-Española conocida como Flamenco"* |

The remaining references (`disonancia:*` and the deeper `fractal_libro:*`
lines) describe content that is in the books but not in the published
index here. We're keeping the refs as honest pointers; once the full
books are indexed they will become directly resolvable.

## Resolving a ref to a meridian chunk

When the full books land in the index, the build script will be updated
to translate every `book_ref` into a structured chunk address:

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
