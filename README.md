# LegalLens AI 🏛️

**An Enterprise-Grade AI Contract Intelligence & Risk Extraction Platform**

LegalLens is an advanced AI platform designed to automate the ingestion, analysis, and interrogation of dense legal contracts. Built with modern GenAI patterns, it utilizes a powerful Retrieval-Augmented Generation (RAG) pipeline to extract critical risks (Liability, Termination, Indemnification) and provides an interactive conversational AI interface backed by strict document citations.

## 🚀 Key Features

*   **Vector Database Architecture:** Powered by a local FAISS vector store, seamlessly managing dense document embeddings for rapid semantic retrieval.
*   **Gemini Vision OCR:** Implements a state-of-the-art fallback pipeline using `PyMuPDF` and Google `gemini-2.5-flash` to physically "read" and extract text from scanned, non-selectable PDF images.
*   **Automated Risk Extraction:** Uses LLM extraction chains to automatically identify and categorize high-risk clauses upon upload, calculating severity and providing exact clause excerpts.
*   **Citation-Backed Chat Assistant:** Eliminates AI hallucination by enforcing strict context bounds. Every answer provided by the AI is backed by explicit citations mapping to the exact page and paragraph of the source document.
*   **Premium "Split-Pane" Interface:** Features a professional, responsive React frontend with a dark slate legal-tech aesthetic, allowing simultaneous document viewing and AI interaction.

## 🛠️ Technology Stack

*   **Backend:** Python, FastAPI, SQLAlchemy (SQLite)
*   **AI / ML:** LangChain, FAISS, Google Generative AI (`models/gemini-embedding-001`, `models/gemini-2.5-flash`)
*   **Frontend:** React 18, TypeScript, Vite, Vanilla CSS, Axios
*   **Authentication:** JWT-based stateless authentication

## ⚙️ Local Setup & Installation

### 1. Backend Initialization
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   * Windows: `.\venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt` (Note: Ensure `bcrypt==3.2.2` is used for `passlib` compatibility).
5. Create a `.env` file in the backend root and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
6. Start the FastAPI server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### 2. Frontend Initialization
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Access the platform at `http://localhost:5173`.

## 🔒 Security & Constraints
*   **Local Processing:** To simulate enterprise data privacy constraints, the FAISS vector database and uploaded PDFs are strictly maintained in local storage (`/uploads`, `/vector_db`) and are isolated from the Git repository.
*   **Auth:** Secured via standard OAuth2 Password Bearer flow.
