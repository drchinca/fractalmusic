"""Frozen DI container — every dependency the route reads is a field."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from chat_bff.protocols import LLM, Retriever
from chat_bff.settings import ChatSettings


@dataclass(frozen=True, slots=True)
class ChatServices:
    retriever: Retriever
    llm_claude: LLM
    llm_ollama: LLM
    similarity: Callable[[str, str], Awaitable[float]]
    settings: ChatSettings
