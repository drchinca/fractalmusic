"""GET /api/audit/{run_id} — the real CEMAF audit trail for one generation
run: every candidate research_loop weighed (corpus vs expert, score, which
one won), not just the pattern that made it into the response.

`run_id` is the same content-addressed cache key already exposed via
`audio_url` in /api/generate*'s response — no new identifier to thread
through, the caller already has it.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from gatople_api.routes.generate import get_services
from gatople_api.services import GatopleServices

router = APIRouter()


class AuditEntryPayload(BaseModel):
    id: str
    type: str
    timestamp: str
    source: str
    payload: dict[str, object]


class AuditTimelineResponse(BaseModel):
    run_id: str
    entries: list[AuditEntryPayload]


@router.get("/api/audit/{run_id}")
async def audit_timeline(
    run_id: str,
    services: Annotated[GatopleServices, Depends(get_services)],
) -> AuditTimelineResponse:
    if services.audit_trail is None:
        raise HTTPException(status_code=503, detail="audit_trail_unavailable")

    entries = await services.audit_trail.get_run_timeline(run_id)
    if not entries:
        raise HTTPException(status_code=404, detail=f"no audit trail for run_id {run_id!r}")

    return AuditTimelineResponse(
        run_id=run_id,
        entries=[
            AuditEntryPayload(
                id=e.id,
                type=e.type.value,
                timestamp=e.timestamp.isoformat(),
                source=e.source,
                payload=dict(e.payload),
            )
            for e in entries
        ],
    )
