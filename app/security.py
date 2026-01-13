# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 14:13:28 2026

@author: NBoyd1
"""

from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)

def require_role(user_role: str, allowed: set[str]) -> bool:
    return user_role in allowed
