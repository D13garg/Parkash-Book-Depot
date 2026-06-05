import pytest
from app.core.email_validation import validate_email_quality


class TestEmailValidation:
    def test_valid_email_passes(self):
        assert validate_email_quality("john.doe@gmail.com") is None

    def test_valid_business_email_passes(self):
        assert validate_email_quality("contacts@gmail.com") is None

    def test_valid_in_domain_passes(self):
        assert validate_email_quality("student@university.in") is None

    def test_disposable_mailinator_blocked(self):
        result = validate_email_quality("test@mailinator.com")
        assert result is not None

    def test_disposable_tempmail_blocked(self):
        result = validate_email_quality("abc@tempmail.com")
        assert result is not None

    def test_fake_pattern_test_blocked(self):
        result = validate_email_quality("test@example.com")
        assert result is not None

    def test_fake_pattern_aaa_blocked(self):
        result = validate_email_quality("aaa@gmail.com")
        assert result is not None

    def test_repeated_chars_blocked(self):
        result = validate_email_quality("aaaa@gmail.com")
        assert result is not None

    def test_single_char_local_blocked(self):
        result = validate_email_quality("a@gmail.com")
        assert result is not None

    def test_invalid_tld_blocked(self):
        result = validate_email_quality("user@domain.fake")
        assert result is not None

    def test_consecutive_dots_blocked(self):
        result = validate_email_quality("user..name@gmail.com")
        assert result is not None

    def test_role_email_noreply_blocked(self):
        result = validate_email_quality("noreply@company.com")
        assert result is not None

    def test_role_email_admin_blocked(self):
        result = validate_email_quality("admin@company.com")
        assert result is not None