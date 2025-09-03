# Israeli Legal AI Chatbot 🏛️

An intelligent legal consultation system that provides AI-powered legal opinions based on Israeli law. This RAG (Retrieval-Augmented Generation) chatbot scrapes, parses, and structures Israeli legal documents to deliver accurate legal guidance through a modern web interface.

## 🚀 Features

- **Legal Document Processing**: Automated scraping and parsing of Hebrew legal texts from Wikisource
- **RAG-Powered AI**: Combines retrieval and generation for accurate legal opinions
- **Hebrew Language Support**: Native Hebrew interface and legal terminology
- **Real-time Chat Interface**: Modern React frontend with responsive design  
- **FastAPI Backend**: High-performance API with proper error handling
- **Vector Search**: Pinecone-based semantic search for relevant legal precedents
- **Legal Citations**: Automatic citation generation with law names and section references

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │◄──►│   FastAPI Backend │◄──►│  Legal Documents │
│   (Hebrew UI)    │    │   (REST API)      │    │   (Wikisource)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │                        ▼                        │
         │              ┌──────────────────┐               │
         │              │   LLM Pipeline   │               │
         │              │ (Gemini + RAG)   │               │
         │              └──────────────────┘               │
         │                        │                        │
         │                        ▼                        │
         │              ┌──────────────────┐               │
         └──────────────►│ Pinecone Vector  │◄──────────────┘
                        │   Database       │
                        └──────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Python 3.8+** - Core backend language
- **FastAPI** - Modern web framework for APIs
- **LangChain** - LLM application framework
- **Google Gemini** - Large language model
- **Pinecone** - Vector database for semantic search
- **BeautifulSoup** - Web scraping for legal documents

### Frontend  
- **React 18** - Modern UI framework
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Axios** - HTTP client for API communication

### Data Processing
- **Sentence Transformers** - Text embeddings
- **Hebrew NLP** - Legal document structure parsing
- **JSON/CSV Output** - Structured data formats

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- Google AI API Key (for Gemini)
- Pinecone API Key (for vector storage)

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/law-agent.git
cd law-agent
```

### 2. Backend Setup
```bash
cd poc/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` file in `poc/backend/`:
```env
GOOGLE_API_KEY=your_google_ai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
```

### 4. Data Processing (First Time Setup)
```bash
# Scrape and process legal documents
python laws-web-scraping.py

# Or use interactive notebook
jupyter notebook web_scraping.ipynb
```

### 5. Start Backend Server
```bash
cd poc/backend/rest-api/app
python main.py
```
Backend runs on `http://localhost:8000`

### 6. Frontend Setup
```bash
cd poc/frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

## 🔧 Development

### Backend Structure
```
poc/backend/
├── fetchers.py           # Web scraping components
├── parsers.py           # Hebrew text parsing
├── storers.py           # Data storage utilities  
├── model_connectors.py  # LLM integrations
├── rest-api/           # FastAPI application
│   ├── app/
│   │   ├── main.py     # API server
│   │   └── llm_pipeline.py  # RAG pipeline
│   ├── models/         # Pydantic models
│   └── dependencies/   # Configuration
└── requirements.txt
```

### Frontend Structure
```
poc/frontend/
├── src/
│   ├── App.jsx         # Main application
│   ├── components/     # React components
│   └── styles/         # CSS files
├── package.json
└── vite.config.js
```

## 📊 Legal Document Processing

The system handles Hebrew legal documents with this structure:
- **Parts (חלק)** - Major document divisions
- **Chapters (פרק)** - Chapter-level organization  
- **Signs (סימן)** - Section groupings
- **Sections (סעיף)** - Individual legal provisions

Example output:
```json
{
  "law_name": "חוק הגנת הפרטיות",
  "part": "חלק א'", 
  "chapter": "פרק ראשון",
  "section": "סעיף 1",
  "text": "בחוק זה, \"מידע אישי\"..."
}
```

## 🎯 Usage

1. **Ask Legal Questions**: Submit Hebrew legal questions through the chat interface
2. **Receive AI Opinions**: Get structured legal opinions with citations
3. **Review Sources**: Each answer includes references to specific laws and sections
4. **Conversational Flow**: Continue discussions for clarification

Example interaction:
```
User: "מה הם זכויות העובד בפיטורין?"
Bot: "על פי חוק הגנת השכר, התשי"ח-1958, סעיף 5..."
```

## 🚦 API Endpoints

- `GET /` - Welcome message and API info
- `GET /health` - Health check endpoint  
- `POST /api/v1/chat` - Submit legal questions
- `GET /api/v1/status` - System status and configuration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`) 
5. Open Pull Request

### Development Guidelines
- Use Hebrew for legal terminology and UI text
- Follow existing code patterns and structure
- Test legal document parsing with various formats
- Ensure proper citation formatting

## ⚖️ Legal Disclaimer

**Important**: This system provides AI-generated legal information for educational and guidance purposes only. It does not constitute professional legal advice. For official legal counsel, consult with a licensed attorney.

התשובות המוצגות כאן הן להנחיה בלבד ואינן מהוות ייעוץ משפטי מקצועי. לצורך ייעוץ משפטי מדויק, יש לפנות לעורך דין מוסמך.

## 🙏 Acknowledgments

- Hebrew Wikisource for legal document sources
- Google AI for Gemini language model
- Pinecone for vector database services
- Israeli legal community for domain expertise
