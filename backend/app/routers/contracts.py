import os
import uuid
import shutil
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.utils import get_current_user
from app.config import settings
from app.services import rag_service

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])

def process_contract_background(contract_id: int, file_path: str, db: Session):
    try:
        # Step 1: Chunk & Index PDF into FAISS
        num_chunks = rag_service.process_and_index_contract(contract_id, file_path)
        
        # Step 2: Auto-extract risks using Gemini RAG
        risks_data = rag_service.extract_automated_risks(contract_id)
        
        # Save risks to DB
        for risk in risks_data:
            db_risk = models.ContractRisk(
                contract_id=contract_id,
                category=risk.get("category", "Other"),
                severity=risk.get("severity", "Medium"),
                explanation=risk.get("explanation", ""),
                clause_text=risk.get("clause_text", "")
            )
            db.add(db_risk)
        
        # Update status
        contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
        if contract:
            contract.status = "indexed"
            
        db.commit()
    except Exception as e:
        contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
        if contract:
            contract.status = "error"
            db.commit()
        print("BACKGROUND RAG ERROR:", str(e))

@router.post("/upload", response_model=schemas.ContractResponse, status_code=201)
def upload_contract(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    ext = ".pdf"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    contract = models.Contract(
        user_id=current_user.id,
        title=title,
        file_path=filename,
        status="processing"
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    
    # Process PDF and query Gemini in background
    background_tasks.add_task(process_contract_background, contract.id, filepath, db)
    
    return contract

@router.get("", response_model=List[schemas.ContractResponse])
def list_contracts(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Contract).filter(models.Contract.user_id == current_user.id).order_by(models.Contract.upload_date.desc()).all()

@router.get("/{contract_id}", response_model=schemas.ContractResponse)
def get_contract(contract_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.post("/{contract_id}/chat", response_model=schemas.ChatSessionResponse)
def chat_with_contract(
    contract_id: int,
    request: schemas.ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id, models.Contract.user_id == current_user.id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
        
    if contract.status != "indexed":
        raise HTTPException(status_code=400, detail="Contract is still processing or failed to index.")
        
    try:
        result = rag_service.query_contract_chat(contract_id, request.message)
        
        chat = models.ChatSession(
            contract_id=contract_id,
            user_message=request.message,
            ai_response=result["answer"],
            citations=json.dumps(result["citations"])
        )
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")
