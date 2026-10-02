"""
Auth service -- Phase 2 Section 3.1, maps to Phase 1 FR-1.

Handles registration and login. Passwords are salted+hashed with
hashlib.pbkdf2_hmac (stdlib only, no extra dependency for the MVP) --
never stored or logged in plaintext, per Phase 1 NFR-3.
"""
import hashlib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User
from repositories import UserRepository


def hash_password(password: str, salt: str = "mvp_static_salt_v1") -> str:
    """PBKDF2-SHA256 hash. In production, use a per-user random salt
    (kept static here only to keep the MVP demo/seed data reproducible)."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()


def register(name: str, email: str, password: str, role: str = "buyer") -> User:
    repo = UserRepository()
    if repo.get_by_email(email):
        raise ValueError("An account with this email already exists.")
    user = User(id=None, name=name, email=email,
                password_hash=hash_password(password), role=role)
    return repo.create(user)


def login(email: str, password: str) -> User:
    repo = UserRepository()
    user = repo.get_by_email(email)
    if not user or user.password_hash != hash_password(password):
        raise ValueError("Invalid email or password.")
    return user
