import os
import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.config import settings

# Initialize a light SQLite database for storing Chat Session metadata
SESSIONS_DB_PATH = "/tmp/neo4j_sessions.db" if os.environ.get("VERCEL") else "./neo4j_sessions.db"


def init_sessions_db():
    conn = sqlite3.connect(SESSIONS_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS GraphSessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            created_at TEXT,
            updated_at TEXT
        );
    """)
    conn.commit()
    conn.close()


init_sessions_db()


class GraphSessionService:
    @staticmethod
    def create_session(user_id: Optional[int] = None, title: str = "New Knowledge Graph Chat") -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(SESSIONS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO GraphSessions (session_id, user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, user_id, title, now, now)
        )
        conn.commit()
        conn.close()
        return {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now
        }

    @staticmethod
    def get_session(session_id: str, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(SESSIONS_DB_PATH)
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("SELECT session_id, title, created_at, updated_at FROM GraphSessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
        else:
            cursor.execute("SELECT session_id, title, created_at, updated_at FROM GraphSessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"session_id": row[0], "title": row[1], "created_at": row[2], "updated_at": row[3]}
        return None

    @staticmethod
    def list_sessions(user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(SESSIONS_DB_PATH)
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("SELECT session_id, title, created_at, updated_at FROM GraphSessions WHERE user_id = ? ORDER BY updated_at DESC", (user_id,))
        else:
            cursor.execute("SELECT session_id, title, created_at, updated_at FROM GraphSessions ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [{"session_id": r[0], "title": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]

    @staticmethod
    def delete_session(session_id: str, user_id: Optional[int] = None) -> bool:
        conn = sqlite3.connect(SESSIONS_DB_PATH)
        cursor = conn.cursor()
        if user_id is not None:
            cursor.execute("DELETE FROM GraphSessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
        else:
            cursor.execute("DELETE FROM GraphSessions WHERE session_id = ?", (session_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
