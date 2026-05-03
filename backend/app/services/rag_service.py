import os
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import fitz
import io
from PIL import Image
import google.generativeai as genai
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from app.config import settings

# Initialize Gemini models
genai.configure(api_key=settings.GEMINI_API_KEY)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.GEMINI_API_KEY
)

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0
)

def _get_faiss_path(contract_id: int):
    return os.path.join(settings.VECTOR_DB_DIR, f"contract_{contract_id}")

def process_and_index_contract(contract_id: int, file_path: str):
    """Parses a PDF, chunks text, creates embeddings, and saves FAISS index."""
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    if not chunks:
        # OCR Fallback for scanned PDFs
        print("Empty chunks. Attempting OCR with Gemini 2.5 Flash Vision...")
        doc = fitz.open(file_path)
        ocr_text = ""
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("jpeg")))
            try:
                response = model.generate_content(["Extract all readable text from this document page exactly as written. If it is empty, return NONE.", img])
                if response.text and "NONE" not in response.text:
                    ocr_text += response.text + "\n\n"
            except Exception as e:
                print(f"OCR failed for page {page_num}: {e}")
                
        if not ocr_text.strip():
            raise ValueError("Could not extract any text from the PDF even with OCR.")
            
        docs = [Document(page_content=ocr_text, metadata={"source": file_path, "page": 0})]
        chunks = text_splitter.split_documents(docs)
        
    
    
    # Generate embeddings and store in FAISS
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(_get_faiss_path(contract_id))
    
    return len(chunks)

def query_contract_chat(contract_id: int, user_query: str) -> dict:
    """Queries the specific contract's FAISS index using RAG."""
    faiss_path = _get_faiss_path(contract_id)
    if not os.path.exists(faiss_path):
        raise ValueError("Contract has not been indexed yet.")
        
    vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    prompt = PromptTemplate.from_template("""
    You are a highly analytical AI Legal Assistant. Your job is to answer questions about the provided legal contract.
    Answer accurately based ONLY on the context below. If you don't know the answer or the context doesn't mention it, state that clearly.
    Do NOT invent or hallucinate legal terms.
    
    <context>
    {context}
    </context>
    
    Question: {input}
    
    Answer:
    """)
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({"input": user_query})
    
    # Extract source documents for citations
    sources = [
        {"page": doc.metadata.get("page", 0), "text": doc.page_content[:200] + "..."}
        for doc in response["context"]
    ]
    
    return {
        "answer": response["answer"],
        "citations": sources
    }

def extract_automated_risks(contract_id: int):
    """Automatically extracts key risks using a structured RAG query."""
    faiss_path = _get_faiss_path(contract_id)
    if not os.path.exists(faiss_path):
        raise ValueError("Contract has not been indexed yet.")
        
    vectorstore = FAISS.load_local(faiss_path, embeddings, allow_dangerous_deserialization=True)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    
    prompt = PromptTemplate.from_template("""
    You are an expert contract lawyer. Review the following contract excerpts and extract high-risk clauses.
    Specifically look for Liability, Termination, and Indemnification clauses.
    
    Respond STRICTLY in valid JSON format with the following structure:
    [
      {{
        "category": "Liability" | "Termination" | "Indemnification",
        "severity": "Low" | "Medium" | "High",
        "explanation": "Brief explanation of why this is a risk",
        "clause_text": "The exact wording of the problematic clause"
      }}
    ]
    
    If a category is missing, do not include it. Return ONLY the JSON array.
    
    <context>
    {context}
    </context>
    """)
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    response = retrieval_chain.invoke({"input": "Extract all key risks regarding liability, termination, and indemnification."})
    
    raw_text = response["answer"].strip()
    # Clean code fences if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("```", 1)[0]
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return []
