import base64
import hashlib
import hmac

SALT = b"dataforge-salt"
ITERATIONS = 120000
ALGORITHM = "sha256"


class PasswordContext:
    def hash(self, password: str) -> str:
        digest = hashlib.pbkdf2_hmac(ALGORITHM, password.encode("utf-8"), SALT, ITERATIONS)
        return base64.b64encode(digest).decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        return hmac.compare_digest(self.hash(password), password_hash)


pwd_context = PasswordContext()
