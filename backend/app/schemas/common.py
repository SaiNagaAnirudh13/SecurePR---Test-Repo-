from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(BaseModel):
    message: str


class UserSummary(ORMModel):
    id: UUID
    email: str
    full_name: str
    role: str


class AuditEntry(ORMModel):
    id: UUID
    actor_id: UUID | None
    action: str
    resource_type: str
    resource_id: str
    details: dict
    created_at: datetime
