"""Pydantic schemas for email configuration."""
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class EmailConfigBase(BaseModel):
    """Base schema for email configuration."""

    smtp_host: str = Field(..., min_length=1, max_length=255)
    smtp_port: int = Field(..., ge=1, le=65535)
    use_tls: bool = True
    use_ssl: bool = False
    smtp_username: str = Field(..., min_length=1, max_length=255)
    from_email: EmailStr
    from_name: Optional[str] = Field(None, max_length=255)

    @model_validator(mode='after')
    def validate_tls_ssl(self):
        """Validate that TLS and SSL are not both enabled."""
        if self.use_tls and self.use_ssl:
            raise ValueError("Cannot use both TLS and SSL. Choose one or neither.")
        return self


class EmailConfigCreate(EmailConfigBase):
    """Schema for creating email configuration."""

    smtp_password: str = Field(..., min_length=1, description="SMTP password (will be encrypted)")


class EmailConfigUpdate(BaseModel):
    """Schema for updating email configuration."""

    smtp_host: Optional[str] = Field(None, min_length=1, max_length=255)
    smtp_port: Optional[int] = Field(None, ge=1, le=65535)
    use_tls: Optional[bool] = None
    use_ssl: Optional[bool] = None
    smtp_username: Optional[str] = Field(None, min_length=1, max_length=255)
    smtp_password: Optional[str] = Field(None, min_length=1, description="New password (will be encrypted)")
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = Field(None, max_length=255)

    @model_validator(mode='after')
    def validate_tls_ssl(self):
        """Validate that TLS and SSL are not both enabled."""
        if self.use_tls is not None and self.use_ssl is not None:
            if self.use_tls and self.use_ssl:
                raise ValueError("Cannot use both TLS and SSL. Choose one or neither.")
        return self


class EmailConfigResponse(EmailConfigBase):
    """Schema for email configuration response."""

    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    # Note: smtp_password_encrypted is NEVER returned

    class Config:
        from_attributes = True


class EmailConfigTestRequest(BaseModel):
    """Schema for testing email configuration."""

    send_test_email: bool = Field(True, description="Send a test email to verify configuration")
    test_recipient: Optional[EmailStr] = Field(None, description="Override recipient for test email")


class EmailConfigTestResponse(BaseModel):
    """Schema for email configuration test response."""

    status: str  # 'success' or 'error'
    message: str
    test_email_sent: bool = False
    sent_to: Optional[str] = None


class SMTPPresetResponse(BaseModel):
    """Schema for SMTP preset response."""

    provider: str
    smtp_host: str
    smtp_port: int
    use_tls: bool
    use_ssl: bool
    note: str


class SMTPPresetsResponse(BaseModel):
    """Schema for all SMTP presets."""

    presets: Dict[str, SMTPPresetResponse]
