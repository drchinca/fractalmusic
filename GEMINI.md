# Fractal Music World (FMW) — Workspace Instructions

This is the project-specific instruction file for the **Sistema Fractal / Fractal Music World** workspace. It bridges Patricio Torres's musical architecture with elite engineering standards, overriding global defaults.

---

## 1. Core Architectural Mandates

1. **A-origin Invariant**: `A` (La menor / Eólico) is the matriarchal tonic. Index 0 = A. Tonic shifts must go through `Wheel(tonic=...)`.
2. **Function-on-the-Wheel**: Notes have no fixed identity; their function is determined by the wheel’s rotation (`Wheel("A").mode_for("D")`).
3. **Two-Disc Model**: The outer disc (roles: glyph, color, clock-position, scale-pattern) never moves. The inner disc (12 notes) rotates.
4. **Pentatonic-First**: Heptatonic modes are derived from pentatonic skeletons, not vice versa.
5. **Canonical Cartas**: The 12 cards are the source of truth for role identity.
6. **BE Owns Logic**: All music-theory, generation, and scoring logic lives in Python (`fractalmusic/`). The web and landing applications are purely inert renderers of pre-baked JSON.

---

## 2. Path & Asset De-duplication Policy

- Do **not** duplicate music theory constants in TypeScript/JavaScript.
- All JSON data assets (e.g., `gatople-data.json`, `progressions-data.json`) must be generated via Python build scripts under `scripts/` and emitted into `web/public/generated/`.
- No new vanilla JavaScript architectures. Legacy vanilla components inside `landing/` must be systematically ported into Vite/React components in `web/` to eliminate double-maintenance.

---

## 3. Git Workflow & Branching Discipline

To maintain high technical integrity, all development must strictly respect these guidelines:

- **Branch Naming**: Must use `<user>/<scope>/<short-desc>` format (e.g., `drchinca/landing/compraclick-assisted-checkout`).
- **Base Branch**: Branches must branch off `develop`. `master` is reserved for stable production releases and must never be committed to or merged into without explicit user instruction.
- **Conventional Commits**: Messages must use:
  - `feat(scope): ...` — for new features.
  - `fix(scope): ...` — for bug fixes.
  - `refactor(scope): ...` — for structural code cleanups.
- **No AI Attribution**: Do not include "AI-generated" or AI attribution headers/signatures in commits or pull request descriptions.
- **Size Limits**:
  - Preferred PR size: **≤ 500 lines** of functional code.
  - Hard cap: **≤ 900 lines** per PR.
  - Split large refactors or migrations into multiple smaller, self-contained branches/PRs.

---

## 4. Pull Request & Commit Creation Protocol

PR descriptions must be calibrated dynamically based on complexity:

- **⚡ Tier 1: Small PRs (< 50 lines / Local Fixes)**
  - Simple `## What & Why` (1-2 sentences) and a direct `## Tests` checklist.
- **🔧 Tier 2: Medium PRs (50 - 300 lines / Feature Additions)**
  - Bulleted `## What & Why`, a markdown table of `## Changes` (Area vs File), and exact copy-pasteable `## Review Steps`.
- **🎯 Tier 3: Large/Epic PRs (> 300 lines / Cross-System Refactors)**
  - Full architectural explanation with a custom ASCII diagram of state/data flow, comprehensive file audit tables, complete passing test logs (`npm run qa`, `uv run pytest`), and an honesty guard section highlighting quirks or limitations.

### Banned Jargon Invariants
Scrub all occurrences of banned terms from PR descriptions and commit messages:
- ❌ *Banned*: `canonical`, `port`, `manager`, `handler`, `wrapper`, `factory`, `scaffold`, `util`, `hydrate`, `materialize`, `reconcile`.
- ✅ *Approved*: `the one blueprint`, `interface`, `client`, `seam`, `core adapter`, `get the app running`.
