from django.conf import settings
from cryptography.fernet import Fernet
from django.core.exceptions import ValidationError
import base64
from django.db import models

class Cryptography:
    def __init__(self):
        try:
            self.key = settings.ENCRYPTION_KEY.encode()
            self.cipher_suite = Fernet(self.key)
        except AttributeError:
            raise ValidationError("ENCRYPTION_KEY must be set in settings.py")

    def encrypt_data(self, data: str) -> str:
        """Encrypt the given string data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            return "Encryption Error"

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt the encrypted string data"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            return "Decryption Error"