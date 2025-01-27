from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import uuid
from .database import init_db
from .models import LoginRequest, SessionRequest, MessageRequest

app = FastAPI()

# Initialize the database
init_db()

# Routes
@app.post("/login")
def login(login_request: LoginRequest):
    if authenticate(login_request.username, login_request.password):
        return {"message": "Login successful", "username": login_request.username}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/create_session")
def create_session(session_request: SessionRequest):
    session_id = str(uuid.uuid4())
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute("INSERT INTO sessions (session_id, admin) VALUES (?, ?)", (session_id, session_request.admin))
    conn.commit()
    conn.close()
    return {"session_id": session_id, "admin": session_request.admin}

@app.post("/join_session")
def join_session(session_id: str):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute("SELECT session_id FROM sessions WHERE session_id = ?", (session_id,))
    result = c.fetchone()
    conn.close()
    if result:
        return {"message": "Session joined successfully", "session_id": session_id}
    raise HTTPException(status_code=404, detail="Session not found")

@app.post("/send_message")
def send_message(message_request: MessageRequest):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (session_id, username, message, is_ai) VALUES (?, ?, ?, ?)",
              (message_request.session_id, message_request.username, message_request.message, message_request.is_ai))
    conn.commit()
    conn.close()
    return {"message": "Message sent successfully"}

@app.get("/get_messages")
def get_messages(session_id: str):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute("SELECT id, username, message, is_ai, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp", (session_id,))
    messages = c.fetchall()
    conn.close()
    return {"messages": messages}

@app.delete("/delete_message/{message_id}")
def delete_message(message_id: int):
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    conn.commit()
    conn.close()
    return {"message": "Message deleted successfully"}

# Helper function for authentication
def authenticate(username: str, password: str):
    if username == "admin" and password == "admin":
        return True
    return False