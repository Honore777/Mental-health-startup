import bcrypt


MAX_BCRYPT_PASSWORD_BYTES = 72


def _is_password_length_valid(password: str) -> bool:
    return len(password.encode("utf-8")) <= MAX_BCRYPT_PASSWORD_BYTES


def hash_password(password: str) -> str:
    if not _is_password_length_valid(password):
        raise ValueError("Password is too long. Maximum supported length is 72 UTF-8 bytes.")
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not _is_password_length_valid(password):
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False
