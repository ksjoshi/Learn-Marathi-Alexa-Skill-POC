# Learn Marathi Alexa Skill - Backend

A modular FastAPI backend for an Alexa Skill that helps in learning Marathi. It features semantic search, RAG (Retrieval-Augmented Generation)-based Q&A, and English-Marathi translation.

## 🚀 Features

- **RAG-based Q&A**: Answers questions about Marathi school curriculum (syllabus) using provided PDF documents.
- **Semantic Search**: Find relevant content in Marathi documents based on meaning, not just keywords.
- **Translation**: English to Marathi and Marathi to English translation using local LLMs.
- **Alexa Integration**: Ready-to-use Lambda handler for integration with Amazon Alexa.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.9+)
- **Database**: [PostgreSQL](https://www.postgresql.org/) with [pgvector](https://github.com/pgvector/pgvector) for vector storage.
- **OCR (Optical Character Recognition)**: 
  - [PyMuPDF](https://pymupdf.readthedocs.io/) (fitz) for PDF processing.
  - [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (via `pytesseract`) for extracting text from scanned PDF pages.
  - [Pillow](https://python-pillow.org/) for image preprocessing (contrast enhancement, sharpening) to improve OCR accuracy.
- **Embeddings**: [Sentence-Transformers](https://www.sbert.net/) (`paraphrase-multilingual-MiniLM-L12-v2`) for multilingual vector representations.
- **LLM (Local)**: [Ollama](https://ollama.com/)
  - `llama3.2` for generating natural language answers.
  - `translategemma` for high-quality English-Marathi translation.
- **Deployment**: AWS Lambda (for Alexa interface).

## 📁 Project Structure

```text
LearnMarathiSkill/
├── app/                  # FastAPI Application
│   ├── api/              # API Route Handlers (Health, RAG, Search, Translate)
│   ├── core/             # Configuration and Settings
│   ├── db/               # Database Connection and Utilities
│   ├── models/           # Pydantic Request/Response Models
│   ├── services/         # Business Logic (Embeddings, RAG, Translation)
│   └── main.py           # API Entry Point
├── lambda/               # Alexa Skill Lambda
│   └── AlexaSkillLambda.py
├── scripts/              # Utility Scripts
│   ├── pdf_to_vector.py  # Ingest PDF -> OCR -> Vector DB
│   └── test_rag.py       # CLI tool for testing RAG
├── requirements.txt      # Python Dependencies
└── marathi_syllabus.pdf  # Sample document
```

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.9+
- PostgreSQL with `pgvector` extension.
- [Ollama](https://ollama.com/) installed and running.
- [Tesseract OCR](https://tesseract-ocr.github.io/tessdoc/Installation.html) installed (for OCR support).

### 2. Pull Ollama Models
```bash
ollama pull llama3.2
ollama pull translategemma
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
Ensure you have a PostgreSQL database named `marathi_knowledge`.

You can quickly start PostgreSQL with `pgvector` using Docker:
```bash
docker run -d \
  --name marathi_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=marathi_knowledge \
  -p 5432:5432 \
  pgvector/pgvector:0.8.2-pg18-trixie
```

Run the following SQL to enable `pgvector` and create the documents table:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    content_english TEXT,
    embedding vector(384),
    metadata JSONB
);
```

### 5. Ingest Documents
Process your Marathi PDFs into the vector database:
```bash
python scripts/pdf_to_vector.py path/to/your/marathi_syllabus.pdf
```

## 🏃 Running the API

Start the FastAPI server:
```bash
python -m app.main
```
The API will be available at `http://localhost:9999`. You can view the interactive documentation at `http://localhost:9999/docs`.

### Testing the API

Once the service is started, you can test it using the following commands:

**Translate API:**
```bash
curl -X POST http://localhost:9999/translate \
     -H "Content-Type: application/json" \
     -d '{"phrase": "How are you?"}'
```
Sample Response:
```json
{"success":true,"translated_text":"तू कसा आहेस?","error":null}
```

**Ask API (RAG):**
```bash
curl -X POST http://localhost:9999/rag/ask \
     -H "Content-Type: application/json" \
     -d '{"query": "how many marks for the full name ?"}'
```
Sample Response:
```json
{"success":true,"answer":"३ गुण असल्याने संपूर्ण नावाची माहिती घेण्यासाठी ३ गुण दिले जातील.","context_used":6,"top_similarity":0.6545276127791653,"error":null}
```

## 🗣 Using with Alexa

The code in `lambda/AlexaSkillLambda.py` is designed to run in AWS Lambda. It communicates with the local API (usually via a tunnel like Ngrok or a VPN during development).

**Supported Intents:**
- `TranslateIntent`: Translates English phrases to Marathi.
- `SchoolIntent`: Asks questions about the school syllabus using the RAG system.

## 🔍 How OCR Works here

The `scripts/pdf_to_vector.py` script handles document ingestion:
1. It attempts native text extraction using `PyMuPDF`.
2. If no text is found (scanned page), it renders the page as a high-resolution image.
3. The image is preprocessed (converted to grayscale, contrast boosted, and sharpened) to help Tesseract.
4. `pytesseract` is called with the `mar` (Marathi) language pack.
5. Extracted text is chunked, translated to English (for better searchability), and stored with its vector embedding.
