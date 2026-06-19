"""Prompt loader. Prompts live as .md files with frontmatter, per the
prompts-as-artifacts rule. The loader strips frontmatter and exposes the
prompt text plus its declared metadata for diagnostics."""

from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


@dataclass(frozen=True, slots=True)
class Prompt:
    name: str
    version: int
    model: str
    template: str  # body, with {passages} / {question} placeholders intact


def load(name: str) -> Prompt:
    """Load a prompt by name (e.g. ``citation_strict`` → citation_strict.md)."""
    path = PROMPTS_DIR / f"{name}.md"
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---"):
        raise ValueError(f"prompt {path} missing frontmatter")
    _, frontmatter, body = raw.split("---", 2)
    meta: dict[str, str] = {}
    for line in frontmatter.strip().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return Prompt(
        name=meta.get("name", name),
        version=int(meta.get("version", "1")),
        model=meta.get("model", "unknown"),
        template=body.strip(),
    )


def render(template: str, *, passages: str, question: str) -> str:
    """Substitute the two placeholders. Other ``{`` characters in the
    template (rare; the prompt avoids them) are left alone — we don't use
    str.format to keep curly braces in code examples safe."""
    return template.replace("{passages}", passages).replace("{question}", question)


def format_passages(chunks: list[dict]) -> str:
    """Render retrieved chunks as a numbered list the LLM can read."""
    lines: list[str] = []
    for i, c in enumerate(chunks, start=1):
        header = (
            f"[{i}] {c['book_hash']}·ch{c['chapter_idx']}§{c['section_idx']}"
            f"¶{c['paragraph_idx']} p.{c['page_start']} — {c['book_title']}"
        )
        lines.append(f"{header}\n{c['text']}")
    return "\n\n".join(lines)
