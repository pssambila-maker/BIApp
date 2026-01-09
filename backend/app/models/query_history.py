from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Store complete query configuration as JSON
    # Structure: {dimension_ids: [...], measure_ids: [...], filters: [...], limit: int}
    query_config = Column(JSONB, nullable=False)

    generated_sql = Column(Text, nullable=False)
    row_count = Column(Integer, nullable=False)
    execution_time_ms = Column(Integer, nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return f"<QueryHistory(id={self.id}, entity_id={self.entity_id}, executed_at={self.executed_at})>"
