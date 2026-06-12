from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime, timezone
from bson import ObjectId


class OTPModel(BaseModel):
    """
    Represents a one-time password document in MongoDB.

    Security design:
    - `code_hash`   : bcrypt hash of the raw 4-digit code — never stored plain
    - `expires_at`  : hard expiry (3 minutes from creation)
    - `used`        : burned on first successful verify — strictly single-use
    - `attempts`    : brute-force guard — invalidated after 5 wrong guesses
    - `purpose`     : 'register' | 'forgot_password' — prevents cross-purpose reuse
    - `pending_data`: encrypted registration payload stored temporarily so we
                      don't create the user until the OTP is verified
    """
    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    code_hash: str                    # bcrypt hash of the 4-digit code
    purpose: str                      # 'register' | 'forgot_password'
    used: bool = False
    attempts: int = 0                 # wrong guess counter
    expires_at: datetime = Field(...)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    pending_data: Optional[dict] = None  # stores hashed register payload temporarily

    @classmethod
    def validate_id(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)

    model_config = {"populate_by_name": True}