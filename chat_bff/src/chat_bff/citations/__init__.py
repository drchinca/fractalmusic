"""Citation parsing + validation. The load-bearing core of the BFF."""

from chat_bff.citations.parser import (
    CITATION_RE,
    CitedClaim,
    ParsedCitation,
    parse_answer,
)
from chat_bff.citations.validator import (
    ValidationOutcome,
    ValidationVerdict,
    validate_answer,
)

__all__ = [
    "CITATION_RE",
    "CitedClaim",
    "ParsedCitation",
    "ValidationOutcome",
    "ValidationVerdict",
    "parse_answer",
    "validate_answer",
]
