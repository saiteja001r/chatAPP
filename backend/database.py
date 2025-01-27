import sqlite3

def init_db():
    conn = sqlite3.connect('chat_app.db')
    c = conn.cursor()
    
    # Drop existing tables (if any) to avoid conflicts
    c.execute("DROP TABLE IF EXISTS sessions")
    c.execute("DROP TABLE IF EXISTS messages")
    
    # Create new tables with the updated schema
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (session_id TEXT PRIMARY KEY, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, admin TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, username TEXT, message TEXT, is_ai BOOLEAN, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()