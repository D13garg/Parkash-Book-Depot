"""
Email validation — Level A
Checks beyond basic format:
- Blocks 500+ known disposable/temporary email domains
- Blocks obviously fake local parts
- Blocks role-based emails
- Validates TLD is real
"""

from typing import Optional
# Disposable email domains — blocked
try:
    from disposable_email_domains import blocklist as DISPOSABLE_DOMAINS
except ImportError:
    DISPOSABLE_DOMAINS = set()

# Role-based prefixes — these are never real users
ROLE_PREFIXES = {
    "admin", "administrator", "noreply", "no-reply", "donotreply",
    "postmaster", "hostmaster", "webmaster", "support", "info",
    "contact", "hello", "help", "sales", "billing", "abuse",
    "security", "root", "system", "mail", "email", "test",
    "demo", "example", "sample", "user", "office",
}

# Obviously fake local parts
FAKE_PATTERNS = {
    "test", "test123", "test1234", "testing", "fake", "fakeemail",
    "temp", "temporary", "throwaway", "trash", "spam", "spamme",
    "asdf", "qwerty", "aaa", "bbb", "ccc", "abc", "xyz",
    "user", "user1", "user123", "person", "someone", "nobody",
    "example", "sample", "demo", "dummy",
}

# Valid TLDs — not exhaustive but covers real ones
VALID_TLDS = {
    "com", "org", "net", "edu", "gov", "mil", "int",
    "in", "co", "io", "ai", "app", "dev", "tech",
    "info", "biz", "name", "pro", "museum", "coop", "aero",
    "uk", "us", "ca", "au", "de", "fr", "jp", "cn", "br",
    "ru", "it", "es", "nl", "se", "no", "dk", "fi", "pl",
    "nz", "za", "mx", "ar", "sg", "hk", "tw", "kr", "in",
    "pk", "bd", "lk", "np", "ae", "sa", "eg", "ng", "ke",
    "me", "tv", "fm", "ly", "to", "cc", "ws", "mobi", "asia",
    "online", "site", "website", "store", "shop", "blog", "cloud",
}


def validate_email_quality(email: str) -> Optional[str]:
    """
    Returns an error message string if the email fails quality checks.
    Returns None if the email passes all checks.
    """
    email = email.lower().strip()

    if "@" not in email:
        return "Invalid email format."

    local, domain = email.rsplit("@", 1)

    # 1. Check disposable domains
    if domain in DISPOSABLE_DOMAINS:
        return "Disposable or temporary email addresses are not allowed. Please use a real email."

    # 2. Check TLD
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    if tld not in VALID_TLDS:
        return f"Email domain '.{tld}' is not recognised. Please use a valid email address."

    # 3. Check role-based prefixes
    if local in ROLE_PREFIXES:
        return "Please use a personal email address, not a role-based one (admin@, noreply@ etc)."

    # 4. Check obviously fake local parts
    if local in FAKE_PATTERNS:
        return "Please use a real email address."

    # 5. Block single-character local parts
    if len(local) < 2:
        return "Email address is too short."

    # 6. Block local parts that are just repeated characters (aaa@, bbb@)
    if len(set(local)) == 1:
        return "Please use a real email address."

    # 7. Block consecutive dots
    if ".." in email:
        return "Invalid email format."

    return None