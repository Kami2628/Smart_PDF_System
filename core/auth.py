import hashlib

from core.database import (
    create_user,
    authenticate_user
)


def hash_password(password):

    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def register_user(username, password):

    username = username.strip()

    if not username:
        return False, "Username is required."

    if not password:
        return False, "Password is required."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    hashed_password = hash_password(
        password
    )

    created = create_user(
        username,
        hashed_password
    )

    if not created:
        return False, "Username already exists."

    return True, "Account created successfully."


def login_user(username, password):

    username = username.strip()

    if not username or not password:
        return None

    hashed_password = hash_password(
        password
    )

    return authenticate_user(
        username,
        hashed_password
    )