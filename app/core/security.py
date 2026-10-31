from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

# 1. Initialize OWASP-recommended Argon2id password hasher
password_hash = PasswordHash.recommended()

# 2. Hash plaintext password using Argon2id
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# 3. Verify plaintext password against stored Argon2id hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# 4. Generate signed JWT Access Token with user identity and session ID
def create_access_token(user_id: int, session_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),       # Subject claim (User ID)
        "session_id": session_id,  # Device session identifier for tracking & eviction
        "exp": expire              # Token expiration timestamp
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

# 5. Decode and validate incoming JWT Access Token
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
