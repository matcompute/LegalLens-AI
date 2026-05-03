from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Contract Schemas ---
class ContractRiskResponse(BaseModel):
    id: int
    category: str
    severity: str
    explanation: str
    clause_text: str
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    user_message: str
    ai_response: str
    citations: str
    created_at: datetime
    class Config:
        from_attributes = True

class ContractResponse(BaseModel):
    id: int
    title: str
    status: str
    file_path: str
    upload_date: datetime
    risks: List[ContractRiskResponse] = []
    chats: List[ChatSessionResponse] = []
    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
