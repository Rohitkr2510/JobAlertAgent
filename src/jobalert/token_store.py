import os
from pathlib import Path

from cryptography.fernet import Fernet


class TokenVault:
    def __init__(self, key_path: Path):
        self.key_path = key_path
        key_path.parent.mkdir(parents=True, exist_ok=True)
        if not key_path.exists():
            key_path.write_bytes(Fernet.generate_key())
            try:
                os.chmod(key_path, 0o600)
            except OSError:
                pass
        self.fernet = Fernet(key_path.read_bytes())

    def encrypt(self, value: str) -> bytes:
        return self.fernet.encrypt(value.encode())

    def decrypt(self, value: bytes) -> str:
        return self.fernet.decrypt(value).decode()
