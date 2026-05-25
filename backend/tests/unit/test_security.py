from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token

class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        assert hash_password("mysecretpassword") != "mysecretpassword"

    def test_correct_password_verifies(self):
        hashed = hash_password("mysecretpassword")
        assert verify_password("mysecretpassword", hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("mysecretpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_different_hashes_for_same_password(self):
        assert hash_password("samepassword") != hash_password("samepassword")

class TestJWT:
    def test_access_token_decode(self):
        token = create_access_token({"sub": "user123", "role": "customer"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    def test_refresh_token_type(self):
        token = create_refresh_token({"sub": "user123"})
        payload = decode_token(token)
        assert payload["type"] == "refresh"

    def test_invalid_token_returns_none(self):
        assert decode_token("this.is.not.valid") is None

    def test_tampered_token_returns_none(self):
        token = create_access_token({"sub": "user123"})
        assert decode_token(token[:-5] + "XXXXX") is None
