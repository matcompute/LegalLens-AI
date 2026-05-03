from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import engine, Base
from app.routers import auth, contracts
from app.config import settings

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LegalLens AI API")

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads dir so frontend can display PDFs
app.mount("/api/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(auth.router)
app.include_router(contracts.router)

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "LegalLens"}
