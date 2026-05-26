from urllib.parse import urlparse


def same_owner(record_owner, current_user):
    return str(record_owner) == str(current_user)


def allowed_callback(target, allowed_hosts):
    parsed = urlparse(target or "")
    if parsed.scheme not in {"http", "https"}:
        return False
    return parsed.hostname in set(allowed_hosts)


def normalize_identifier(value):
    return str(value or "").strip().lower()
