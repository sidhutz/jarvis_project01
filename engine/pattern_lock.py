import hashlib
import json
import os
import secrets


PATTERN_FILE = "pattern_lock.json"
MIN_PATTERN_LENGTH = 4


def _hash_pattern(pattern, salt):
    return hashlib.sha256(f"{salt}:{pattern}".encode("utf-8")).hexdigest()


def _load_pattern_data():
    if not os.path.exists(PATTERN_FILE):
        return None

    try:
        with open(PATTERN_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        return None


def _save_pattern_data(pattern):
    salt = secrets.token_hex(16)
    data = {
        "salt": salt,
        "pattern_hash": _hash_pattern(pattern, salt),
    }

    with open(PATTERN_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)


def is_pattern_set():
    data = _load_pattern_data()
    return bool(data and data.get("salt") and data.get("pattern_hash"))


def is_valid_pattern(pattern):
    return isinstance(pattern, str) and len(pattern.split("-")) >= MIN_PATTERN_LENGTH


def verify_pattern(pattern):
    data = _load_pattern_data()
    if not data:
        return False

    salt = data.get("salt")
    pattern_hash = data.get("pattern_hash")
    if not salt or not pattern_hash:
        return False

    return secrets.compare_digest(_hash_pattern(pattern, salt), pattern_hash)


def set_pattern(pattern):
    if is_pattern_set():
        return {"ok": False, "message": "Pattern already set. Use change pattern."}

    if not is_valid_pattern(pattern):
        return {"ok": False, "message": "Connect at least 4 dots."}

    _save_pattern_data(pattern)
    return {"ok": True, "message": "Pattern set successfully."}


def unlock_pattern(pattern):
    if not is_pattern_set():
        return {"ok": True, "message": "No pattern is set."}

    if verify_pattern(pattern):
        return {"ok": True, "message": "Pattern unlocked."}

    return {"ok": False, "message": "Wrong pattern."}


def change_pattern(current_pattern, new_pattern):
    if not is_pattern_set():
        return set_pattern(new_pattern)

    if not verify_pattern(current_pattern):
        return {"ok": False, "message": "Current pattern is wrong."}

    if not is_valid_pattern(new_pattern):
        return {"ok": False, "message": "Connect at least 4 dots."}

    _save_pattern_data(new_pattern)
    return {"ok": True, "message": "Pattern changed successfully."}


def remove_pattern(current_pattern):
    if not is_pattern_set():
        return {"ok": True, "message": "No pattern is set."}

    if not verify_pattern(current_pattern):
        return {"ok": False, "message": "Current pattern is wrong."}

    try:
        os.remove(PATTERN_FILE)
    except FileNotFoundError:
        pass

    return {"ok": True, "message": "Pattern removed successfully."}
