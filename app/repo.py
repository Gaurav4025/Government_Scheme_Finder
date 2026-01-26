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
