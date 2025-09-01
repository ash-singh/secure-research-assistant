import sqlite3
import os
from config import DATABASE_FILE

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS docs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE
        )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS chunks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id INTEGER,
            text TEXT,
            FOREIGN KEY(doc_id) REFERENCES docs(id) ON DELETE CASCADE
        )"""
    )
    conn.commit()
    conn.close()


def add_doc(filename, chunks):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO docs(filename) VALUES (?)", (filename,))
    doc_id = cur.execute(
        "SELECT id FROM docs WHERE filename=?", (filename,)
    ).fetchone()[0]
    for c in chunks:
        cur.execute("INSERT INTO chunks(doc_id, text) VALUES (?, ?)", (doc_id, c))
    conn.commit()
    conn.close()


def remove_doc(filename):
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM docs WHERE filename=?", (filename,))
    conn.commit()
    conn.close()


def list_docs():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, filename FROM docs").fetchall()
    conn.close()
    return [{"id": r[0], "filename": r[1]} for r in rows]


def get_all_chunks():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT c.text, d.filename FROM chunks c JOIN docs d ON c.doc_id=d.id"
    ).fetchall()
    conn.close()
    return [{"text": r[0], "source": r[1]} for r in rows]


def reset_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks")
    cur.execute("DELETE FROM docs")
    conn.commit()
    conn.close()
