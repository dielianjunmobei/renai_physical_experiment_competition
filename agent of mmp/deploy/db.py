"""
数理方法 Agent 用户数据库
记录所有问答、错误、反馈，用于后续升级分析
"""
import sqlite3
import os
import json
import time
import uuid
import hashlib
import secrets as py_secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_logs.db")


def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _hash_password(password, salt=None):
    if salt is None:
        salt = py_secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    ).hex()
    return salt, hashed


def _ensure_column(conn, table, column, definition):
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in columns:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            display_name TEXT,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT,
            chapter TEXT,
            provider TEXT,
            model TEXT,
            tokens_input INTEGER DEFAULT 0,
            tokens_output INTEGER DEFAULT 0,
            response_time_ms INTEGER DEFAULT 0,
            error TEXT,
            feedback TEXT,
            rag_chunks_used TEXT,
            question_length INTEGER DEFAULT 0,
            answer_length INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            start_time TEXT NOT NULL,
            end_time TEXT,
            total_questions INTEGER DEFAULT 0,
            total_errors INTEGER DEFAULT 0,
            total_tokens_input INTEGER DEFAULT 0,
            total_tokens_output INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS error_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            question TEXT,
            error_type TEXT,
            error_message TEXT,
            traceback TEXT
        );

        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            rating TEXT NOT NULL,
            comment TEXT,
            FOREIGN KEY (interaction_id) REFERENCES interactions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_interactions_session ON interactions(session_id);
        CREATE INDEX IF NOT EXISTS idx_interactions_chapter ON interactions(chapter);
        CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);
        CREATE INDEX IF NOT EXISTS idx_errors_timestamp ON error_log(timestamp);
        CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    """)
    _ensure_column(conn, "sessions", "user_id", "INTEGER")
    _ensure_column(conn, "sessions", "last_seen", "TEXT")
    _ensure_column(conn, "interactions", "user_id", "INTEGER")
    _ensure_column(conn, "error_log", "user_id", "INTEGER")
    _ensure_column(conn, "feedback", "user_id", "INTEGER")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id)")
    conn.commit()
    conn.close()


def create_user(username, password, display_name=""):
    username = (username or "").strip()
    display_name = (display_name or "").strip() or username
    if not username:
        raise ValueError("用户名不能为空")
    if len(username) < 3:
        raise ValueError("用户名至少需要 3 个字符")
    if not password or len(password) < 6:
        raise ValueError("密码至少需要 6 个字符")

    salt, password_hash = _hash_password(password)
    conn = _get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO users
               (username, display_name, password_salt, password_hash, role, created_at)
               VALUES (?, ?, ?, ?, 'student', ?)""",
            (username, display_name, salt, password_hash, datetime.now().isoformat()),
        )
        conn.commit()
        user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError("用户名已存在")
    finally:
        conn.close()
    return get_user_by_id(user_id)


def authenticate_user(username, password):
    username = (username or "").strip()
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND is_active=1",
        (username,),
    ).fetchone()
    if not row:
        conn.close()
        return None
    salt, password_hash = _hash_password(password or "", row["password_salt"])
    if not py_secrets.compare_digest(password_hash, row["password_hash"]):
        conn.close()
        return None
    conn.execute(
        "UPDATE users SET last_login=? WHERE id=?",
        (datetime.now().isoformat(), row["id"]),
    )
    conn.commit()
    conn.close()
    return get_user_by_id(row["id"])


def get_user_by_id(user_id):
    conn = _get_conn()
    row = conn.execute(
        "SELECT id, username, display_name, role, created_at, last_login FROM users WHERE id=?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def start_session(user_id=None):
    sid = datetime.now().strftime("ses_%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:6]
    conn = _get_conn()
    conn.execute(
        "INSERT INTO sessions (session_id, start_time, last_seen, user_id) VALUES (?, ?, ?, ?)",
        (sid, datetime.now().isoformat(), datetime.now().isoformat(), user_id)
    )
    conn.commit()
    conn.close()
    return sid


def touch_session(session_id):
    if not session_id:
        return
    conn = _get_conn()
    conn.execute(
        "UPDATE sessions SET last_seen=? WHERE session_id=? AND end_time IS NULL",
        (datetime.now().isoformat(), session_id),
    )
    conn.commit()
    conn.close()


def get_active_session_count(active_minutes=5):
    conn = _get_conn()
    cutoff = datetime.fromtimestamp(time.time() - active_minutes * 60).isoformat()
    count = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE end_time IS NULL AND COALESCE(last_seen, start_time) >= ?",
        (cutoff,),
    ).fetchone()[0]
    conn.close()
    return count


def end_session(session_id, total_q, total_err, ti, to):
    conn = _get_conn()
    conn.execute(
        """UPDATE sessions SET end_time=?, total_questions=?, total_errors=?,
           total_tokens_input=?, total_tokens_output=?
           WHERE session_id=?""",
        (datetime.now().isoformat(), total_q, total_err, ti, to, session_id)
    )
    conn.commit()
    conn.close()


def log_interaction(session_id, question, answer, chapter, provider, model,
                    tokens_input, tokens_output, response_time_ms, error=None,
                    rag_chunks=None, user_id=None):
    conn = _get_conn()
    conn.execute(
        """INSERT INTO interactions
           (session_id, timestamp, question, answer, chapter, provider, model,
            tokens_input, tokens_output, response_time_ms, error,
            rag_chunks_used, question_length, answer_length, user_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (session_id, datetime.now().isoformat(), question, answer, chapter,
         provider, model, tokens_input, tokens_output, response_time_ms, error,
         json.dumps(rag_chunks, ensure_ascii=False) if rag_chunks else None,
         len(question) if question else 0, len(answer) if answer else 0,
         user_id)
    )
    conn.commit()
    conn.close()


def log_error(session_id, question, error_type, error_message, traceback_str="", user_id=None):
    conn = _get_conn()
    conn.execute(
        """INSERT INTO error_log (session_id, timestamp, question, error_type, error_message, traceback, user_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (session_id, datetime.now().isoformat(), question, error_type, error_message, traceback_str, user_id)
    )
    conn.commit()
    conn.close()


def log_feedback(interaction_id, session_id, rating, comment="", user_id=None):
    conn = _get_conn()
    conn.execute(
        "INSERT INTO feedback (interaction_id, session_id, timestamp, rating, comment, user_id) VALUES (?, ?, ?, ?, ?, ?)",
        (interaction_id, session_id, datetime.now().isoformat(), rating, comment, user_id)
    )
    conn.commit()
    conn.close()


def get_user_recent_interactions(user_id, limit=20):
    """Return recent successful interactions for restoring a user's chat history."""
    if not user_id:
        return []
    conn = _get_conn()
    rows = conn.execute(
        """SELECT timestamp, question, answer, chapter
           FROM interactions
           WHERE user_id=? AND question IS NOT NULL AND answer IS NOT NULL
           ORDER BY timestamp DESC
           LIMIT ?""",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def get_user_interaction_count(user_id):
    if not user_id:
        return 0
    conn = _get_conn()
    count = conn.execute(
        "SELECT COUNT(*) FROM interactions WHERE user_id=?",
        (user_id,),
    ).fetchone()[0]
    conn.close()
    return count


def get_user_interactions(user_id):
    """Return all successful conversation records belonging to one user."""
    if not user_id:
        return []
    conn = _get_conn()
    rows = conn.execute(
        """SELECT timestamp, question, answer, chapter
           FROM interactions
           WHERE user_id=? AND question IS NOT NULL AND answer IS NOT NULL
           ORDER BY timestamp ASC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ==================== Analytics Queries ====================

def get_chapter_stats():
    """各章节提问统计"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT chapter, COUNT(*) as cnt, SUM(tokens_input) as ti, SUM(tokens_output) as to_tokens FROM interactions WHERE chapter IS NOT NULL GROUP BY chapter ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_error_stats():
    """错误统计"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT error_type, COUNT(*) as cnt FROM error_log GROUP BY error_type ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_daily_stats():
    """每日用量统计"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT date(timestamp) as day, COUNT(*) as questions, SUM(tokens_input) as ti, SUM(tokens_output) as to_tokens FROM interactions GROUP BY day ORDER BY day DESC LIMIT 30"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_recent_errors(limit=20):
    """最近错误"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT timestamp, question, error_type, error_message FROM error_log ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_unanswered_questions():
    """未回答成功的问题（有错误的）"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT question, error, timestamp, chapter FROM interactions WHERE error IS NOT NULL ORDER BY timestamp DESC LIMIT 50"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_total_stats():
    """总体统计"""
    conn = _get_conn()
    total_q = conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
    total_err = conn.execute("SELECT COUNT(*) FROM interactions WHERE error IS NOT NULL").fetchone()[0]
    total_ti = conn.execute("SELECT COALESCE(SUM(tokens_input),0) FROM interactions").fetchone()[0]
    total_to = conn.execute("SELECT COALESCE(SUM(tokens_output),0) FROM interactions").fetchone()[0]
    sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    conn.close()
    return {
        "total_questions": total_q,
        "total_errors": total_err,
        "error_rate": f"{total_err/max(total_q,1)*100:.1f}%",
        "total_input_tokens": total_ti,
        "total_output_tokens": total_to,
        "total_sessions": sessions,
    }


def get_feedback_stats():
    """反馈统计"""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT rating, COUNT(*) as cnt FROM feedback GROUP BY rating"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_stats():
    """用户统计"""
    conn = _get_conn()
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    active_users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM sessions WHERE user_id IS NOT NULL").fetchone()[0]
    recent_users = conn.execute(
        """SELECT id, username, display_name, role, created_at, last_login
           FROM users
           ORDER BY COALESCE(last_login, created_at) DESC
           LIMIT 20"""
    ).fetchall()
    conn.close()
    return {
        "total_users": total_users,
        "active_users": active_users,
        "recent": [dict(r) for r in recent_users],
    }


# ==================== Init on import ====================
init_db()
