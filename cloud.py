import os
import sqlite3
from datetime import datetime, timezone

LOCAL_DB = "jarvis.db"
FIREBASE_KEY_FILE = "firebase_key.json"
CHAT_COLLECTION = "chats"
DEFAULT_SESSION_TITLE = "Previous chats"

_firestore_db = None
_firebase_error = None


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat()


def _connect_local_db():
    con = sqlite3.connect(LOCAL_DB)
    con.row_factory = sqlite3.Row
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TEXT NOT NULL,
            cloud_id TEXT,
            synced INTEGER DEFAULT 0
        )
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_sessions(
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    columns = {
        row["name"]
        for row in con.execute("PRAGMA table_info(chat_history)").fetchall()
    }
    if "session_id" not in columns:
        con.execute("ALTER TABLE chat_history ADD COLUMN session_id TEXT")
    con.commit()
    _migrate_old_chats(con)
    return con


def _make_session_id():
    return "chat_" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _migrate_old_chats(con):
    old_count = con.execute(
        "SELECT COUNT(*) AS total FROM chat_history WHERE session_id IS NULL OR session_id = ''"
    ).fetchone()["total"]

    if old_count == 0:
        return

    row = con.execute(
        "SELECT created_at FROM chat_history WHERE session_id IS NULL OR session_id = '' ORDER BY datetime(created_at) ASC, id ASC LIMIT 1"
    ).fetchone()
    created_at = row["created_at"] if row else _utc_now_iso()
    updated_at = _utc_now_iso()
    session_id = "default"

    con.execute(
        """
        INSERT OR IGNORE INTO chat_sessions(id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, DEFAULT_SESSION_TITLE, created_at, updated_at),
    )
    con.execute(
        """
        UPDATE chat_history
        SET session_id = ?
        WHERE session_id IS NULL OR session_id = ''
        """,
        (session_id,),
    )
    con.commit()


def create_chat_session(title="New chat"):
    created_at = _utc_now_iso()
    session_id = _make_session_id()

    with _connect_local_db() as con:
        con.execute(
            """
            INSERT INTO chat_sessions(id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, title, created_at, created_at),
        )
        con.commit()

    return {
        "id": session_id,
        "title": title,
        "created_at": created_at,
        "updated_at": created_at,
    }


def ensure_chat_session(session_id=None, title="New chat"):
    with _connect_local_db() as con:
        if session_id:
            row = con.execute(
                "SELECT id, title, created_at, updated_at FROM chat_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if row:
                return dict(row)

    return create_chat_session(title)


def _title_from_message(message):
    title = " ".join((message or "").strip().split())
    if not title:
        return "New chat"
    return title[:42] + ("..." if len(title) > 42 else "")


def list_chat_sessions():
    with _connect_local_db() as con:
        rows = con.execute(
            """
            SELECT
                s.id,
                CASE
                    WHEN s.title = 'New chat' THEN COALESCE(
                        (
                            SELECT h2.message
                            FROM chat_history h2
                            WHERE h2.session_id = s.id
                            ORDER BY datetime(h2.created_at) ASC, h2.id ASC
                            LIMIT 1
                        ),
                        s.title
                    )
                    ELSE s.title
                END AS title,
                s.created_at,
                s.updated_at,
                COUNT(h.id) AS message_count
            FROM chat_sessions s
            LEFT JOIN chat_history h ON h.session_id = s.id
            GROUP BY s.id
            ORDER BY datetime(s.updated_at) DESC
            """
        ).fetchall()

    sessions = []
    for row in rows:
        item = dict(row)
        item["title"] = _title_from_message(item["title"])
        sessions.append(item)
    return sessions


def _get_firestore():
    global _firestore_db, _firebase_error

    if _firestore_db is not None:
        return _firestore_db

    if _firebase_error is not None:
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        credential_path = os.getenv("FIREBASE_KEY_PATH", FIREBASE_KEY_FILE)
        if not os.path.exists(credential_path):
            _firebase_error = f"Firebase key not found: {credential_path}"
            return None

        if not firebase_admin._apps:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred)

        _firestore_db = firestore.client()
        return _firestore_db
    except Exception as exc:
        _firebase_error = str(exc)
        print("Firebase unavailable:", exc)
        return None


def save_chat(user, message, response, session_id=None):
    created_at = _utc_now_iso()
    session = ensure_chat_session(session_id, _title_from_message(message))
    session_id = session["id"]
    cloud_id = None
    synced = 0

    firestore_db = _get_firestore()
    if firestore_db is not None:
        try:
            doc_ref = firestore_db.collection(CHAT_COLLECTION).add(
                {
                    "user": user,
                    "message": message,
                    "response": response,
                    "created_at": created_at,
                    "session_id": session_id,
                    "session_title": session["title"],
                }
            )[1]
            cloud_id = doc_ref.id
            synced = 1
        except Exception as exc:
            print("Cloud chat save failed, saving locally:", exc)

    with _connect_local_db() as con:
        con.execute(
            """
            INSERT INTO chat_history(user, message, response, created_at, cloud_id, synced, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user, message, response, created_at, cloud_id, synced, session_id),
        )
        con.execute(
            "UPDATE chat_sessions SET updated_at = ? WHERE id = ?",
            (created_at, session_id),
        )
        con.commit()

    return session_id


def sync_unsynced_chats():
    firestore_db = _get_firestore()
    if firestore_db is None:
        return 0

    synced_count = 0
    with _connect_local_db() as con:
        rows = con.execute(
            """
            SELECT id, user, message, response, created_at, session_id
            FROM chat_history
            WHERE synced = 0
            ORDER BY created_at ASC
            """
        ).fetchall()

        for row in rows:
            try:
                doc_ref = firestore_db.collection(CHAT_COLLECTION).add(
                    {
                        "user": row["user"],
                        "message": row["message"],
                        "response": row["response"],
                        "created_at": row["created_at"],
                        "session_id": row["session_id"],
                    }
                )[1]
                con.execute(
                    "UPDATE chat_history SET synced = 1, cloud_id = ? WHERE id = ?",
                    (doc_ref.id, row["id"]),
                )
                synced_count += 1
            except Exception as exc:
                print("Cloud chat sync stopped:", exc)
                break

        con.commit()

    return synced_count


def _local_history(limit, session_id=None):
    with _connect_local_db() as con:
        if session_id:
            rows = con.execute(
                """
                SELECT *
                FROM (
                    SELECT user, message, response, created_at, synced, session_id, id
                    FROM chat_history
                    WHERE session_id = ?
                    ORDER BY datetime(created_at) DESC, id DESC
                    LIMIT ?
                )
                ORDER BY datetime(created_at) ASC, id ASC
                """,
                (session_id, limit),
            ).fetchall()
        else:
            rows = con.execute(
                """
                SELECT *
                FROM (
                    SELECT user, message, response, created_at, synced, session_id, id
                    FROM chat_history
                    ORDER BY datetime(created_at) DESC, id DESC
                    LIMIT ?
                )
                ORDER BY datetime(created_at) ASC, id ASC
                """,
                (limit,),
            ).fetchall()

    history = []
    for row in rows:
        item = dict(row)
        item.pop("id", None)
        history.append(item)
    return history


def get_history(limit=100, session_id=None):
    sync_unsynced_chats()

    firestore_db = _get_firestore()
    if firestore_db is None:
        return _local_history(limit, session_id)

    try:
        chats = firestore_db.collection(CHAT_COLLECTION).stream()
        history = []
        for chat in chats:
            item = chat.to_dict()
            if session_id and item.get("session_id") != session_id:
                continue
            item["cloud_id"] = chat.id
            item["synced"] = 1
            history.append(item)

        if history:
            history.sort(key=lambda item: item.get("created_at", ""))
            return history[-limit:]
    except Exception as exc:
        print("Cloud chat history failed, loading local history:", exc)

    return _local_history(limit, session_id)


def cloud_status():
    return {
        "enabled": _get_firestore() is not None,
        "error": _firebase_error,
    }
