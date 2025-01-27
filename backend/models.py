from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class SessionRequest(BaseModel):
    admin: str

class MessageRequest(BaseModel):
    session_id: str
    username: str
    message: str
    is_ai: bool = False