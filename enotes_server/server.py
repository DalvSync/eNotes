from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import sqlite3
import uvicorn
import datetime

app = FastAPI(title="DalvID Cloud API")

DEFAULT_QUOTA_BYTES = 20 * 1024 * 1024 

def init_db():
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    c.execute(f'''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, auth_hash TEXT, max_storage_bytes INTEGER DEFAULT {DEFAULT_QUOTA_BYTES})''')
    c.execute('''CREATE TABLE IF NOT EXISTS notes 
                 (id INTEGER PRIMARY KEY, user_id INTEGER, title TEXT, payload TEXT, updated_at TEXT, UNIQUE(user_id, title))''')
    conn.commit()
    conn.close()

init_db()

class AuthModel(BaseModel):
    username: str
    auth_hash: str

class NoteModel(BaseModel):
    title: str
    payload_b64: str

def get_current_user(username: str = Header(...), auth_hash: str = Header(..., alias="auth-hash")):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    user = c.execute("SELECT id FROM users WHERE username=? AND auth_hash=?", (username, auth_hash)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Невірний логін або пароль")
    return user[0]

@app.post("/register")
def register(data: AuthModel):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, auth_hash) VALUES (?, ?)", (data.username, data.auth_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Користувач з таким DalvID вже існує")
    conn.close()
    return {"status": "success"}

@app.post("/login")
def login(data: AuthModel):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    user = c.execute("SELECT id FROM users WHERE username=? AND auth_hash=?", (data.username, data.auth_hash)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=401, detail="Невірний пароль DalvID")
    return {"status": "success"}

@app.get("/notes")
def list_notes(user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    
    max_bytes = c.execute("SELECT max_storage_bytes FROM users WHERE id=?", (user_id,)).fetchone()[0]
    notes = c.execute("SELECT title, updated_at, LENGTH(payload) FROM notes WHERE user_id=?", (user_id,)).fetchall()
    
    total_bytes = sum((n[2] or 0) for n in notes)
    conn.close()
    
    return {
        "notes": [{"title": n[0], "updated_at": n[1], "size": n[2]} for n in notes],
        "total_bytes": total_bytes,
        "max_bytes": max_bytes
    }

@app.post("/notes")
def upload_note(note: NoteModel, user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()

    max_bytes = c.execute("SELECT max_storage_bytes FROM users WHERE id=?", (user_id,)).fetchone()[0]
    
    current_usage = c.execute("SELECT SUM(LENGTH(payload)) FROM notes WHERE user_id=? AND title != ?", (user_id, note.title)).fetchone()[0] or 0
    new_payload_size = len(note.payload_b64)
    
    if current_usage + new_payload_size > max_bytes:
        conn.close()
        raise HTTPException(status_code=400, detail="Перевищено ліміт хмарного сховища DalvID (20 МБ)!")
    
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    c.execute('''INSERT INTO notes (user_id, title, payload, updated_at) VALUES (?, ?, ?, ?)
                 ON CONFLICT(user_id, title) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at''',
              (user_id, note.title, note.payload_b64, now))
    conn.commit()
    conn.close()
    return {"status": "saved", "updated_at": now}

@app.get("/notes/{title}")
def download_note(title: str, user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    note = c.execute("SELECT payload, updated_at FROM notes WHERE user_id=? AND title=?", (user_id, title)).fetchone()
    conn.close()
    if not note: raise HTTPException(status_code=404, detail="Нотатку не знайдено")
    return {"title": title, "payload_b64": note[0], "updated_at": note[1]}

@app.delete("/notes/{title}")
def delete_note(title: str, user_id: int = Depends(get_current_user)):
    conn = sqlite3.connect("cloud_notes.db")
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE user_id=? AND title=?", (user_id, title))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

@app.get("/ping")
def ping(): return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)