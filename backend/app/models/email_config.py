"""Email configuration model for SMTP settings."""
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class EmailConfiguration(Base):
    """Email configuration model for user-specific SMTP settings."""

    __tablename__ = "email_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # One config per user
        index=True
    )

    # SMTP server settings
    smtp_host = Column(String(255), nullable=False)
    smtp_port = Column(Integer, nullable=False, default=587)
    use_tls = Column(Boolean, nullable=False, default=True)
    use_ssl = Column(Boolean, nullable=False, default=False)

    # Authentication
    smtp_username = Column(String(255), nullable=False)
    smtp_password_encrypted = Column(String(512), nullable=False)  # Fernet encrypted

    # From email settings
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(255), nullable=True)

    # Relationships
    owner = relationship("User", back_populates="email_config")

    # Ensure one config per user
    __table_args__ = (
        UniqueConstraint('owner_id', name='uix_email_config_owner'),
    )

    def __repr__(self):
        return f"<EmailConfiguration(id={self.id}, smtp_host={self.smtp_host}, from_email={self.from_email})>"
