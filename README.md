# Web Chat

RAG-powered chatbot with FastAPI, Gemini AI, and ChromaDB. Upload documents, ask questions, get intelligent answers.

## Demo

https://github.com/neetpalsingh/rag-chatbot-gemini-chromadb-flask/raw/main/demo.mp4

> Demo video showing chat interface, document upload, and AI responses.

## Features

- Google Gemini 2.5 Flash for responses
- Multi-document support (PDF/TXT)
- Session-based conversation memory
- ChromaDB vector search with 3072-dim embeddings
- FastAPI async backend
- Markdown formatting in responses
- Document categories (HR, Finance, Legal, Compliance, General)
- **Adjustable LLM settings** - Control Top K, Temperature, and Top P in real-time

## Quick Start

### Requirements

- Python 3.11+
- Gemini API key from https://aistudio.google.com/apikey

### Setup

Clone the repo:
```bash
git clone https://github.com/yourusername/rag-chatbot-gemini-chromadb-flask.git
cd rag-chatbot-gemini-chromadb-flask
```

Create virtual environment:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create `.env` file in `backend/`:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_CHAT_MODEL=models/gemini-2.5-flash
GEMINI_EMBED_MODEL=models/gemini-embedding-2
EMBEDDING_DIMENSION=3072
SECRET_KEY=your_secret_key_here
```

Run the server:
```bash
python main.py
```

Open http://localhost:8000/chat.html

## Usage

### Chat Page (chat.html)
Upload documents using the paperclip icon, then ask questions. The bot retrieves relevant chunks and generates answers using your uploaded content.

Click "New Chat" to clear the session and start fresh.

### Settings Panel
Click the settings icon (⚙️) to adjust:

**Top K** (1-20, default 5)
How many document chunks to retrieve. Higher = more context, slower response.

**Temperature** (0.0-2.0, default 0.7)
Controls randomness. Lower = focused and consistent, Higher = creative and varied.

**Top P** (0.0-1.0, default 0.95)
Nucleus sampling threshold. Lower = deterministic, Higher = diverse word choices.

Settings are saved in browser localStorage and persist across sessions.

### Documents Page (documents.html)
Manage all uploaded files. Select a category (HR, Finance, Legal, Compliance, General) before uploading. View all documents in a table and delete when needed.

## Tech Stack

**Backend**
- FastAPI (async web framework)
- Google Gemini API (LLM and embeddings)
- ChromaDB (vector database)
- SQLite (metadata storage)
- PyPDF2 (PDF parsing)

**Frontend**
- Vanilla JavaScript
- CSS3
- Font Awesome

## Project Structure

```
backend/
├── api/routes/        # FastAPI endpoints
├── services/          # Core logic (chat, embedding, retrieval, memory)
├── database/          # ChromaDB and SQLite managers
├── models/            # Pydantic schemas
├── prompts/           # Prompt templates
├── utils/             # PDF/text readers, validators
├── memory/            # Session JSON files
└── main.py            # Entry point

frontend/
├── chat.html          # Chat interface
├── documents.html     # Document manager
├── css/chat.css       # Styles
└── js/
    ├── api.js         # API client
    ├── chat.js        # Chat logic
    └── documents.js   # Document logic
```

## Configuration

You can change defaults in `backend/config.py`:

```python
CHUNK_SIZE_WORDS = 200          # Words per chunk
CHUNK_OVERLAP_WORDS = 50        # Overlap between chunks
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
MAX_FILE_SIZE_MB = 10
```

LLM parameters (Top K, Temperature, Top P) are now controlled from the UI settings panel, not config files.

## How It Works

**Upload Flow**
1. PDF/TXT file uploaded
2. Split into 200-word chunks with 50-word overlap
3. Each chunk converted to 3072-dim embedding
4. Stored in ChromaDB (one collection per file)
5. Metadata saved in SQLite

**Query Flow**
1. User asks a question
2. Question converted to embedding
3. Top K similar chunks retrieved from ChromaDB (adjustable in settings)
4. Retrieved chunks + last 10 messages sent to Gemini
5. LLM generates answer with temperature and top_p from settings

**Session Memory**
- Stored as JSON files in `backend/memory/`
- Last 10 messages included in context
- Persists across page refreshes
- Clear with "New Chat" button

## Troubleshooting

**API key errors**
Make sure `.env` exists in `backend/` folder. No quotes or spaces around the key.

**Port already in use**
Change port in `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Rate limit (429 error)**
Gemini free tier has limits. Wait a bit and retry, or upgrade to paid tier.

**Session memory not working**
Check that `backend/memory/` folder exists and browser cookies are enabled.

## License

MIT

## Contributing

Fork the repo, make changes, and submit a PR.

## Contact

Issues: https://github.com/neetpalsingh/rag-chatbot-gemini-chromadb-flask/issues
Email: neetpalsingh750@gmail.com

