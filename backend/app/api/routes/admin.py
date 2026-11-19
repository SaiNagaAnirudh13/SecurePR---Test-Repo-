from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import DbSession, ReportingUser
from app.models import AuditLog
from app.schemas.common import AuditEntry

router = APIRouter()


@router.get("/audit-logs", response_model=list[AuditEntry])
def list_audit_logs(
    db: DbSession,
    user: ReportingUser,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[AuditLog]:
    return list(
        db.scalars(
            select(AuditLog).order_by(AuditLog.created_at.desc()).offset(offset).limit(limit)
        ).all()
    )
