# gatople_api

The HTTP API over the `fractalmusic` engine — theory, generation, rendering,
and citation-strict chat. This is not a chat-only backend: `/api/generate*`
runs the full research-loop → realize → render pipeline, `/api/chat` answers
questions grounded in the indexed Sistema Fractal corpus.

## Run it

```bash
make api-install   # from repo root — installs this package in editable mode
make api           # runs on :8002 (foreground)
# or, to run this together with the web app:
make dev           # gatople_api on :8002 + web on :5174, logs tailed together
```

Boot itself is slow (~30s observed before the server starts accepting
requests, `/healthz` included) — production wiring loads the full meridian
BM25 + vector index (two ~150MB pickles under `~/.meridian/library` by
default) synchronously before the app is built. This isn't a hang; give it
time before assuming something's broken.

Once running, the full interactive API contract is live at
`http://127.0.0.1:8002/docs` (Swagger UI) — that page is generated directly
from the route signatures below and is always current; treat it as the
source of truth over this table.

## Routes

| Method | Path | What it does |
|---|---|---|
| `GET` | `/healthz` | Liveness probe. |
| `POST` | `/api/chat` | Citation-strict Q&A over the indexed fractal book corpus. |
| `GET` | `/api/generate/options` | The closed sets (tonics, modes, flavors) the FE renders as dropdowns. |
| `POST` | `/api/generate` | Runs the fractalmusic research loop, renders a real WAV, returns the web playback payload. |
| `POST` | `/api/generate/strudel` | Same as `/api/generate`, plus book-guided Strudel live-coding source. |

## Architecture

`gatople_api.services.GatopleServices` is a frozen, slotted DI container —
routes pull it via `Depends(get_services)` reading `request.app.state.services`.
`gatople_api.protocols` defines structural `Protocol`s (`Retriever`, `LLM`,
`Similarity`) so the route layer never imports `cemaf`/`meridian` directly.
`gatople_api.bootstrap.build_services()` is the one production composition
root; tests build their own `GatopleServices` from fakes and override the
dependency per-test.

## Config

Env-loaded via `gatople_api.settings.ChatSettings` (prefix `CHAT_BFF_`,
`.env`-file supported). See that file for the full field list — the load-
bearing ones are `anthropic_api_key` (chat needs it; falls back to Ollama
without it) and `index_dir` (defaults to `~/.meridian/library`).

## Tests

```bash
make api-test          # unit + integration (fast — this is what CI-equivalent local checks run)
cd gatople_api && uv run pytest -m eval   # golden-set calibration eval (slow, run explicitly)
```

## Known gap

`pyproject.toml` depends on `cemaf` and `meridian-library` via local
filesystem paths (`../../../iccha_context_multi_agent/{cemaf,meridian_library}`)
that are not a pushed git repository. It only installs and runs on machines
with those sibling repos present, and can't currently be checked out and
installed by any hosted CI runner or dependency-update bot as a result.
