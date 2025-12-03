import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from BackendDeveloper.models import User
from BackendDeveloper.database import get_db

# ===========================
# CONFIGURATION
# ===========================
SECRET_KEY = "SECRET123"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer auth
security = HTTPBearer()


# ===========================
# PASSWORD FUNCTIONS
# ===========================
def hash_password(password: str) -> str:
    """
    Hash a password with bcrypt. Truncate to 72 chars (bcrypt limit).
    """
    return pwd_context.hash(password[:72])


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    """
    return pwd_context.verify(password[:72], password_hash)


# ===========================
# JWT TOKEN FUNCTIONS
# ===========================
def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with expiration.
    Requires 'sub' in payload.
    """
    if "sub" not in data:
        raise ValueError("Payload must contain 'sub'")

    payload = data.copy()
    payload["sub"] = str(
        payload["sub"]
    )  # ensure string for JWT (* I was running into problems)
    expire = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode JWT token and validate.
    Raises HTTPException on error.
    """
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = decoded.get("sub")
        if not sub or not isinstance(sub, str):
            raise HTTPException(
                status_code=401, detail="Invalid token: 'sub' missing or invalid"
            )
        return decoded

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# ===========================
# DEPENDENCY: CURRENT USER
# ===========================
def get_current_user(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]
    decoded = decode_token(token)

    user_id = int(decoded["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
