"""Email configuration API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.email_config import EmailConfiguration
from app.schemas.email_config import (
    EmailConfigCreate,
    EmailConfigUpdate,
    EmailConfigResponse,
    EmailConfigTestRequest,
    EmailConfigTestResponse,
    SMTPPresetResponse,
    SMTPPresetsResponse
)
from app.services.email_service import EmailService
from app.utils.encryption import get_encryption_service
from app.api.auth import get_current_user

router = APIRouter(prefix="/email-config", tags=["email-config"])


@router.get("", response_model=EmailConfigResponse)
async def get_email_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's email configuration.

    Returns:
        EmailConfigResponse: User's SMTP configuration (password excluded)
    """
    result = await db.execute(
        select(EmailConfiguration).where(EmailConfiguration.owner_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found. Please configure SMTP settings first."
        )

    return config


@router.post("", response_model=EmailConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_email_config(
    config_data: EmailConfigCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create or update email configuration for the current user.

    If configuration already exists, it will be updated.
    SMTP password is encrypted before storage.
    """
    encryption = get_encryption_service()

    # Check if config already exists
    result = await db.execute(
        select(EmailConfiguration).where(EmailConfiguration.owner_id == current_user.id)
    )
    existing_config = result.scalar_one_or_none()

    # Encrypt password
    encrypted_password = encryption.encrypt(config_data.smtp_password)

    if existing_config:
        # Update existing configuration
        existing_config.smtp_host = config_data.smtp_host
        existing_config.smtp_port = config_data.smtp_port
        existing_config.use_tls = config_data.use_tls
        existing_config.use_ssl = config_data.use_ssl
        existing_config.smtp_username = config_data.smtp_username
        existing_config.smtp_password_encrypted = encrypted_password
        existing_config.from_email = config_data.from_email
        existing_config.from_name = config_data.from_name

        await db.commit()
        await db.refresh(existing_config)
        return existing_config
    else:
        # Create new configuration
        new_config = EmailConfiguration(
            owner_id=current_user.id,
            smtp_host=config_data.smtp_host,
            smtp_port=config_data.smtp_port,
            use_tls=config_data.use_tls,
            use_ssl=config_data.use_ssl,
            smtp_username=config_data.smtp_username,
            smtp_password_encrypted=encrypted_password,
            from_email=config_data.from_email,
            from_name=config_data.from_name
        )

        db.add(new_config)
        await db.commit()
        await db.refresh(new_config)
        return new_config


@router.put("", response_model=EmailConfigResponse)
async def update_email_config(
    config_update: EmailConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update existing email configuration.

    Only provided fields will be updated.
    If smtp_password is provided, it will be re-encrypted.
    """
    # Get existing config
    result = await db.execute(
        select(EmailConfiguration).where(EmailConfiguration.owner_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found. Use POST to create."
        )

    # Update fields
    update_data = config_update.model_dump(exclude_unset=True)

    # Handle password encryption
    if 'smtp_password' in update_data:
        encryption = get_encryption_service()
        encrypted_password = encryption.encrypt(update_data['smtp_password'])
        update_data['smtp_password_encrypted'] = encrypted_password
        del update_data['smtp_password']

    for field, value in update_data.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return config


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete email configuration.

    This will prevent sending of scheduled reports until reconfigured.
    """
    result = await db.execute(
        select(EmailConfiguration).where(EmailConfiguration.owner_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found"
        )

    await db.delete(config)
    await db.commit()


@router.post("/test", response_model=EmailConfigTestResponse)
async def test_email_config(
    test_request: EmailConfigTestRequest = EmailConfigTestRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Test SMTP configuration and optionally send a test email.

    This verifies:
    1. SMTP connection can be established
    2. Authentication succeeds
    3. (Optional) Test email can be sent
    """
    email_service = EmailService()

    try:
        # Test connection
        test_result = await email_service.test_connection(current_user.id, db)

        if test_result["status"] == "error":
            return EmailConfigTestResponse(
                status="error",
                message=test_result["message"],
                test_email_sent=False
            )

        # Send test email if requested
        if test_request.send_test_email:
            recipient = test_request.test_recipient or current_user.email

            test_email_html = """
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>SMTP Configuration Test</h2>
                <p>This is a test email from your BI Platform.</p>
                <p><strong>Status:</strong> ✓ SMTP configuration is working correctly!</p>
                <p>You can now create scheduled reports and they will be delivered to recipients.</p>
                <hr>
                <p style="font-size: 11px; color: #666;">
                    This test was triggered from the Email Configuration settings.
                </p>
            </body>
            </html>
            """

            try:
                await email_service.send_report_email(
                    user_id=current_user.id,
                    recipients=[recipient],
                    subject="BI Platform - SMTP Test Email",
                    body_html=test_email_html,
                    db=db
                )

                return EmailConfigTestResponse(
                    status="success",
                    message="SMTP connection successful and test email sent",
                    test_email_sent=True,
                    sent_to=recipient
                )
            except Exception as e:
                return EmailConfigTestResponse(
                    status="error",
                    message=f"SMTP connection successful but failed to send test email: {str(e)}",
                    test_email_sent=False
                )

        return EmailConfigTestResponse(
            status="success",
            message="SMTP connection successful",
            test_email_sent=False
        )

    except ValueError as e:
        return EmailConfigTestResponse(
            status="error",
            message=str(e),
            test_email_sent=False
        )
    except Exception as e:
        return EmailConfigTestResponse(
            status="error",
            message=f"Unexpected error: {str(e)}",
            test_email_sent=False
        )


@router.get("/presets", response_model=SMTPPresetsResponse)
async def get_smtp_presets():
    """
    Get SMTP configuration presets for common email providers.

    Returns presets for Gmail, Outlook, Office365, Yahoo, and custom SMTP.
    This is a public endpoint (no authentication required).
    """
    email_service = EmailService()
    presets = email_service.get_smtp_presets()

    # Convert to response format
    preset_responses = {
        provider: SMTPPresetResponse(
            provider=provider,
            **config
        )
        for provider, config in presets.items()
    }

    return SMTPPresetsResponse(presets=preset_responses)
