from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UUIDSchema(BaseModel):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
