"""Encryption utilities for sensitive data."""
import os
from typing import Optional

from cryptography.fernet import Fernet

from app.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data using Fernet."""

    def __init__(self):
        """Initialize encryption service with key from settings or environment."""
        # Get encryption key from settings or generate one
        self.encryption_key = self._get_or_generate_key()
        self.cipher = Fernet(self.encryption_key)

    def _get_or_generate_key(self) -> bytes:
        """Get encryption key from settings or generate a new one."""
        key = settings.encryption_key

        if key:
            # Key provided in settings
            if isinstance(key, str):
                key = key.encode()
            return key

        # Generate a new key (for development only)
        print("WARNING: No ENCRYPTION_KEY found in settings. Generating temporary key.")
        print("WARNING: This key will NOT persist across restarts!")
        print("WARNING: Set ENCRYPTION_KEY in .env for production.")
        return Fernet.generate_key()

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""

        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string.

        Args:
            encrypted_text: Encrypted string (base64 encoded)

        Returns:
            Decrypted plaintext string

        Raises:
            ValueError: If decryption fails
        """
        if not encrypted_text:
            return ""

        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    @staticmethod
    def generate_key() -> str:
        """
        Generate a new Fernet encryption key.

        Returns:
            Base64-encoded encryption key as string

        Usage:
            >>> key = EncryptionService.generate_key()
            >>> print(f"Add to .env: ENCRYPTION_KEY={key}")
        """
        key = Fernet.generate_key()
        return key.decode()


# Global instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get global encryption service instance."""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service
