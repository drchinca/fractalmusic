"""Citation parsing + validation. The load-bearing core of the BFF."""

from gatople_api.citations.parser import (
    CITATION_RE,
    CitedClaim,
    ParsedCitation,
    parse_answer,
)
from gatople_api.citations.validator import (
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
