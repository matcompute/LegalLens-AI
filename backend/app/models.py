from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    contracts = relationship("Contract", back_populates="user", cascade="all, delete-orphan")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="processing")  # processing, indexed, error
    upload_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="contracts")
    risks = relationship("ContractRisk", back_populates="contract", cascade="all, delete-orphan")
    chats = relationship("ChatSession", back_populates="contract", cascade="all, delete-orphan")


class ContractRisk(Base):
    __tablename__ = "contract_risks"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    category = Column(String(100), nullable=False)  # Liability, Termination, Indemnification
    severity = Column(String(50), default="Medium")  # Low, Medium, High
    explanation = Column(Text, nullable=False)
    clause_text = Column(Text, nullable=False)
    
    contract = relationship("Contract", back_populates="risks")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    citations = Column(Text, default="")  # JSON string of source chunks
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    contract = relationship("Contract", back_populates="chats")
