---
name: audit-fractalmusic
description: Run a comprehensive audit of the fractalmusic repo through four independent reviewer lenses — fractal-theorist (book/Sistema fidelity), music-ux-voice (everyday musician language), audio-engineer (DSP/render correctness), and simplifier (lean-keeper). Produces a single ranked punch-list. Use this skill before merging any non-trivial PR, after a feature lands, or any time you suspect the code is drifting from what the app should be. Read-only — surfaces findings, doesn't edit code.
---

# Audit Fractalmusic

Run the four project-local reviewer agents in parallel, gather their outputs, rank the findings into one punch-list the developer can act on.

## Purpose

Catch drift across four independent dimensions in one command:
- **Sistema fidelity** — does the code honor *El Sistema Fractal*'s cardinal invariants?
- **Voice of the musician** — would a Spanish-speaking guitar teacher understand the UI?
- **Render correctness** — does the WAV pipeline produce clean, well-staged audio?
- **Lean-keeping** — is the work earning its place, or piling on ceremony?

Each lens is independent. None of them substitutes for the others.

## Core Functionality

Spawn four agents *in parallel* — `fractal-theorist`, `music-ux-voice`, `audio-engineer`, `simplifier` — feed each a focused brief, collect their findings, and synthesize into a single ranked report.

## Rules

### Critical Requirements

- Spawn all four agents in **a single message** (parallel `Agent` tool calls). Don't serialize.
- Each agent gets a brief tuned to their lens — see "Briefs" below. Don't dump the whole repo at them.
- Synthesize, don't concatenate. The output is ONE ranked list, not four separate reports.
- Read-only. The skill never writes code. The user decides what lands.

### Format

Final output is markdown:
- `## Audit summary` — 2-line headline ("X critical, Y polish, Z simplify")
- `## P0 — Cardinal violations` (anything fractal-theorist flagged "Cardinal")
- `## P0 — Audio bugs` (anything audio-engineer flagged "Bug")
- `## P1 — Strong drift / Critical UX`
- `## P2 — Polish + simplify`
- Each finding: file:line, one-line problem, one-line fix proposal

Cap at ≤ 700 words. Findings only — no preamble, no praise.

### Validation

- Did all four agents return non-empty output?
- Are there any duplicate findings across agents (same file:line) that should be merged?
- Is every finding actionable (has a file:line + a fix)?

## Briefs (use exactly these prompts when spawning)

### fractal-theorist

> Audit the fractalmusic repo for fidelity to *El Sistema Fractal* cardinal invariants. Focus areas: `fractalmusic/wheel.py`, `fractalmusic/modes.py`, `fractalmusic/dodecamundo.py`, `fractalmusic/cartas.py`, `fractalmusic/generate/`, `fractalmusic/render/`, `web/src/composer/`, `web/src/gatople/`. Look for hard-coded note→mode bindings, tonic implied from context, FE doing theory, missing book citations on claims, penta/hepta branches, carta canonical-order violations. Report under 400 words. Findings only.

### music-ux-voice

> Read every user-facing string in `web/src/`. Files: `web/src/shell/AppShell.tsx`, `web/src/composer/ComposerPanel.tsx`, `web/src/gatople/**/*.tsx`, `web/src/strudel/StrudelPanel.tsx`, `web/src/chat/**/*.tsx`. You are a Spanish-speaking guitar teacher in Buenos Aires. Flag anything that wouldn't land for you on first read. Replacement copy in Spanish. Under 350 words.

### audio-engineer

> Review `fractalmusic/render/` (engine.py, synth.py, reverb.py, soundfont.py) and `chat_bff/src/chat_bff/routes/generate.py` (the render call site). Catch synthesis bugs, gain staging, polyphony budget, sample-rate mismatches, IR convolution mistakes, normalization, envelope discontinuities, FluidSynth corner cases, cache key correctness. Report under 400 words. Bug / Perf / Correctness-gap priority.

### simplifier

> Lean-keeper review of all changes in the recent feature work — `fractalmusic/render/`, `chat_bff/src/chat_bff/routes/generate.py`, `web/src/composer/`, the new audit/agent files in `.claude/`. One-dev music app — does this earn its place? Flag ceremony, premature abstractions, BrightHive-grade rules misapplied. Under 400 words.

## Usage Workflow

1. Confirm the four agent files exist at `.claude/agents/{fractal-theorist,music-ux-voice,audio-engineer,simplifier}.md`. If any are missing, error out — don't run a partial audit.
2. Spawn all four agents in parallel with the briefs above.
3. Collect each agent's findings.
4. Deduplicate findings that hit the same file:line across agents (the highest-priority lens wins, but mention which lenses agreed).
5. Rank into P0 / P1 / P2 buckets per the format above.
6. Output the synthesized report.
7. Do NOT spawn additional agents. Do NOT edit code.

## Validation Checklist

- [ ] All four agents returned findings
- [ ] Duplicate findings merged
- [ ] Every finding has file:line
- [ ] Every finding has a one-line fix proposal
- [ ] Total output ≤ 700 words
- [ ] No code edits made
