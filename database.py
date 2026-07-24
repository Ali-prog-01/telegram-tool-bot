import sqlite3
import threading
from config import DB_PATH

_lock = threading.Lock()


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """جدول‌های مورد نیاز رو در صورت نبود، می‌سازه."""
    with _lock:
        conn = get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                is_sent INTEGER DEFAULT 0
            )
            """
        )
        conn.commit()
        conn.close()


def add_reminder(chat_id: int, text: str, remind_at_iso: str) -> int:
    with _lock:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO reminders (chat_id, text, remind_at) VALUES (?, ?, ?)",
            (chat_id, text, remind_at_iso),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id


def get_pending_reminders():
    with _lock:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM reminders WHERE is_sent = 0 ORDER BY remind_at ASC"
        ).fetchall()
        conn.close()
        return rows


def get_user_reminders(chat_id: int):
    with _lock:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM reminders WHERE chat_id = ? AND is_sent = 0 ORDER BY remind_at ASC",
            (chat_id,),
        ).fetchall()
        conn.close()
        return rows


def mark_reminder_sent(reminder_id: int):
    with _lock:
        conn = get_connection()
        conn.execute("UPDATE reminders SET is_sent = 1 WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()


def delete_reminder(reminder_id: int, chat_id: int) -> bool:
    with _lock:
        conn = get_connection()
        cur = conn.execute(
            "DELETE FROM reminders WHERE id = ? AND chat_id = ?", (reminder_id, chat_id)
        )
        conn.commit()
        deleted = cur.rowcount > 0
        conn.close()
        return deleted
