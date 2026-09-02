"""Frozen DI container — every dependency the route reads is a field."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from cemaf.audit.protocols import AuditLog, AuditTrail
from fractalmusic.generate import ExpertClient, PatternCorpus

from gatople_api.protocols import LLM, Retriever
from gatople_api.settings import ChatSettings


@dataclass(frozen=True, slots=True)
class GatopleServices:
    retriever: Retriever
    llm_claude: LLM
    llm_ollama: LLM
    similarity: Callable[[str, str], Awaitable[float]]
    settings: ChatSettings
    expert: ExpertClient
    llm_expert: ExpertClient
    corpus: PatternCorpus
    # Optional: generation still works with no audit trail wired (PS-14
    # graceful degradation) — test files that don't care about audit don't
    # need to change. Production wiring (bootstrap.py) always provides both.
    audit_log: AuditLog | None = None
    audit_trail: AuditTrail | None = None
