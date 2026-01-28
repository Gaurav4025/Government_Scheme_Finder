import json
from app.sqlite_db import get_conn


def list_conversations():
    conn = get_conn()
    rows = conn.execute("""
        SELECT id, title, created_at
        FROM conversations
        ORDER BY id DESC
    """).fetchall()
    conn.close()
    return rows


def create_conversation(title="New Chat"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def get_conversation(conversation_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT id, title FROM conversations WHERE id=?",
        (conversation_id,)
    ).fetchone()
    conn.close()
    return row


def get_messages(conversation_id: int):
    conn = get_conn()
    rows = conn.execute("""
        SELECT role, content, sources_json, created_at
        FROM messages
        WHERE conversation_id=?
        ORDER BY id ASC
    """, (conversation_id,)).fetchall()
    conn.close()

    msgs = []
    for r in rows:
        sources = []
        if r["sources_json"]:
            try:
                sources = json.loads(r["sources_json"])
            except:
                sources = []
        msgs.append({
            "role": r["role"],
            "content": r["content"],
            "sources": sources,
            "created_at": r["created_at"]
        })
    return msgs


def add_message(conversation_id: int, role: str, content: str, sources=None):
    sources_json = json.dumps(sources or [])
    conn = get_conn()
    conn.execute("""
        INSERT INTO messages (conversation_id, role, content, sources_json)
        VALUES (?, ?, ?, ?)
    """, (conversation_id, role, content, sources_json))
    conn.commit()
    conn.close()


def rename_conversation(conversation_id: int, title: str):
    conn = get_conn()
    conn.execute("UPDATE conversations SET title=? WHERE id=?", (title, conversation_id))
    conn.commit()
    conn.close()


def delete_conversation(conversation_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM messages WHERE conversation_id=?", (conversation_id,))
    conn.execute("DELETE FROM conversations WHERE id=?", (conversation_id,))
    conn.commit()
    conn.close()


# User authentication functions
def create_user(user_id: str, email: str, password_hash: str):
    conn = get_conn()
    try:
        conn.execute("INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)", (user_id, email, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        return None  # Email already exists
    finally:
        conn.close()
    return user_id


def get_user_by_email(email: str):
    conn = get_conn()
    row = conn.execute("SELECT id, email, password_hash FROM users WHERE email=?", (email,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id: str):
    conn = get_conn()
    row = conn.execute("SELECT id, email FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return row


# Profile functions
def save_profile(user_id: str, name: str, dob: str, state: str, income: int, category: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO profiles (user_id, name, dob, state, income, category, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (user_id, name, dob, state, income, category))
    conn.commit()
    conn.close()


def get_profile(user_id: str):
    conn = get_conn()
    row = conn.execute("SELECT name, dob, state, income, category FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return row


# Document functions
def save_document(doc_id: str, user_id: str, doc_type: str, file_path: str, extracted_text: str):
    conn = get_conn()
    conn.execute("INSERT INTO documents (id, user_id, doc_type, file_path, extracted_text) VALUES (?, ?, ?, ?, ?)",
                 (doc_id, user_id, doc_type, file_path, extracted_text))
    conn.commit()
    conn.close()


def get_user_documents(user_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT id, doc_type FROM documents WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return rows


def get_document_text(user_id: str):
    conn = get_conn()
    rows = conn.execute("SELECT extracted_text FROM documents WHERE user_id=?", (user_id,)).fetchall()
    conn.close()
    return " ".join([row["extracted_text"] for row in rows if row["extracted_text"]])
