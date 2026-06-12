"""
OTP Service

Security model:
- Codes are 4 digits, generated with secrets.randbelow (cryptographically secure)
- Code is bcrypt-hashed before storage — DB dump reveals nothing usable
- Constant-time bcrypt verify — no timing attacks
- Max 5 wrong attempts → OTP invalidated (brute force: 5/10000 = 0.05% before lockout)
- Max 3 send attempts per email per hour → blocks OTP flooding
- Single-use: burned immediately on first success
- TTL: 3 minutes, enforced both in code and by MongoDB TTL index
- Purpose-scoped: 'register' OTP cannot satisfy 'forgot_password' and vice versa
"""

import secrets
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext
from app.core.exceptions import (
    BadRequestException,
    TooManyRequestsException,
    UnauthorizedException,
)

logger = logging.getLogger(__name__)

OTP_EXPIRE_MINUTES = 3
MAX_ATTEMPTS = 5          # wrong guesses before OTP is burned
MAX_SENDS_PER_HOUR = 3    # OTP sends per email per hour

# Separate bcrypt context for OTPs — lower cost (8) is fine for 4-digit codes
# since they already expire in 3 min and are rate-limited
_otp_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=8)


def _generate_code() -> str:
    """Returns a cryptographically secure 4-digit string, zero-padded."""
    return f"{secrets.randbelow(10000):04d}"


def _hash_code(code: str) -> str:
    return _otp_ctx.hash(code)


def _verify_code(code: str, code_hash: str) -> bool:
    """Constant-time bcrypt compare — no timing leak."""
    return _otp_ctx.verify(code, code_hash)


class OTPService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.col = db["otps"]

    # ── Rate limit: max 3 sends per email per hour ────────────────────────────

    async def _check_send_rate_limit(self, email: str, purpose: str) -> None:
        one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        count = await self.col.count_documents({
            "email": email,
            "purpose": purpose,
            "created_at": {"$gte": one_hour_ago},
        })
        if count >= MAX_SENDS_PER_HOUR:
            raise TooManyRequestsException(
                f"Too many verification emails sent. Please wait before requesting another."
            )

    # ── Invalidate any existing unused OTPs for this email+purpose ───────────

    async def _invalidate_existing(self, email: str, purpose: str) -> None:
        await self.col.update_many(
            {"email": email, "purpose": purpose, "used": False},
            {"$set": {"used": True}}
        )

    # ── Create OTP ────────────────────────────────────────────────────────────

    async def create_otp(
        self,
        email: str,
        purpose: str,
        pending_data: Optional[dict] = None,
    ) -> str:
        """
        Generate a new OTP, store it hashed, return the raw code (to email).
        Enforces send rate limit and invalidates any prior OTP for this email+purpose.
        """
        await self._check_send_rate_limit(email, purpose)
        await self._invalidate_existing(email, purpose)

        code = _generate_code()
        code_hash = _hash_code(code)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)

        doc = {
            "email": email,
            "code_hash": code_hash,
            "purpose": purpose,
            "used": False,
            "attempts": 0,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc),
            "pending_data": pending_data,
        }
        await self.col.insert_one(doc)

        # Never log the code itself
        logger.info(f"OTP created [email={email}, purpose={purpose}]")
        return code

    # ── Verify OTP ────────────────────────────────────────────────────────────

    async def verify_otp(self, email: str, code: str, purpose: str) -> Optional[dict]:
        """
        Verify a submitted OTP code.

        Returns `pending_data` (may be None) on success.
        Raises on any failure — wrong code, expired, used, too many attempts.

        On success, marks the OTP as used (single-use).
        On wrong code, increments attempt counter and burns OTP at max attempts.
        """
        now = datetime.now(timezone.utc)

        # Find the latest unused, non-expired OTP for this email+purpose
        otp_doc = await self.col.find_one(
            {
                "email": email,
                "purpose": purpose,
                "used": False,
                "expires_at": {"$gt": now},
            },
            sort=[("created_at", -1)],
        )

        if otp_doc is None:
            # Could be expired, used, or never existed — same error either way (no enumeration)
            raise UnauthorizedException(
                "Invalid or expired verification code. Please request a new one."
            )

        # Check attempt count BEFORE verifying — prevents timing oracle
        if otp_doc["attempts"] >= MAX_ATTEMPTS:
            await self.col.update_one(
                {"_id": otp_doc["_id"]},
                {"$set": {"used": True}}
            )
            raise UnauthorizedException(
                "Too many incorrect attempts. Please request a new verification code."
            )

        # Constant-time bcrypt compare
        if not _verify_code(code, otp_doc["code_hash"]):
            new_attempts = otp_doc["attempts"] + 1
            if new_attempts >= MAX_ATTEMPTS:
                # Burn it
                await self.col.update_one(
                    {"_id": otp_doc["_id"]},
                    {"$set": {"used": True, "attempts": new_attempts}}
                )
                raise UnauthorizedException(
                    "Too many incorrect attempts. Please request a new verification code."
                )
            else:
                await self.col.update_one(
                    {"_id": otp_doc["_id"]},
                    {"$inc": {"attempts": 1}}
                )
                remaining = MAX_ATTEMPTS - new_attempts
                raise UnauthorizedException(
                    f"Incorrect code. {remaining} attempt{'s' if remaining != 1 else ''} remaining."
                )

        # ✅ Code is correct — burn it immediately (single-use)
        await self.col.update_one(
            {"_id": otp_doc["_id"]},
            {"$set": {"used": True}}
        )

        logger.info(f"OTP verified [email={email}, purpose={purpose}]")
        return otp_doc.get("pending_data")