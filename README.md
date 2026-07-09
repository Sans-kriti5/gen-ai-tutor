# 📚 AI Academic Tutor

> An AI-powered academic assistant that helps students learn, revise, and prepare for exams through intelligent conversation, structured reasoning, and tool-based assistance — built with **Google Gemini**, **LangChain**, **FAISS**, and **Streamlit**.

---

## 🖼️ Overview

AI Academic Tutor is a full-featured, RAG-powered study assistant that reads your PDF study materials and lets you interact with them through multiple learning modes — from conversational Q&A to automated quiz generation, sequential study workflows, and a tool-calling AI agent.

---

## 🚀 Features

### 🤖 Core AI Capabilities
| Feature | Description |
|---|---|
| **RAG Q&A Chat** | Ask questions from uploaded PDFs using Gemini + FAISS retrieval |
| **Chain-of-Thought Reasoning** | View the model's step-by-step thinking process in a collapsible expander |
| **Multi-Role Tutor** | Switch between Teacher, Examiner, Study Coach, and Subject Expert modes |
| **Conversational Memory** | Chat history is passed to Gemini so follow-up questions work naturally |

### 📖 Study Tools (Tabs)
| Tab | Feature |
|---|---|
| 💬 **Chat Q&A** | Main RAG conversational interface |
| 📝 **Revision Notes** | Generate structured bullet-point notes from a topic |
| ⚡ **Quick Quiz** | Generate 5 MCQ questions on any topic from the document |
| 📅 **Study Planner** | Create a day-by-day learning roadmap for a topic |
| 📄 **Summarizer** | Get a 150-word concept overview |
| 🔗 **Sequential Chain** | Run the `Topic → Explanation → Notes → Quiz` LangChain LCEL pipeline |
| 🤖 **Agent Assistant** | Interact with a tool-calling LangChain Agent |

### 🧰 LangChain Agent Tools
- **Calculator** — Safely evaluates math expressions (e.g., packet delay, bandwidth calculations)
- **Summarizer** — Condenses long academic text into a target word count
- **Study Planner** — Generates a structured study schedule given a topic and duration

### 👤 Personalization & Memory
- **Student Profile** — Save Name, Roll Number, and Department in the sidebar
- **Learning History** — Persistent log of all topics studied, activities taken, and timestamps saved to `user_profile.json`
- **Personalized Prompts** — Responses are automatically tailored using the student's profile

### 🎨 UI & Accessibility
- **Dark / Light Theme** — Toggle via sidebar; styles loaded from `styles/dark.css` and `styles/light.css`
- **Dynamic PDF Upload** — Upload any PDF from the sidebar to index and query it instantly
- **Per-PDF FAISS Indexes** — Each uploaded document maintains its own vector database under `vector_db/<pdf_name>/`

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **LLM** | Google Gemini 2.5 Flash (`ChatGoogleGenerativeAI`) |
| **Embeddings** | `GoogleGenerativeAIEmbeddings` (gemini-embedding-001) |
| **Vector Store** | FAISS (per-document indexing) |
| **Orchestration** | LangChain (LCEL, Agents, Tools, Chains) |
| **PDF Parsing** | PyPDF |
| **Frontend** | Streamlit |
| **Styling** | Vanilla CSS (dark + light themes) |
| **Environment** | Python-dotenv |

---

## 📂 Project Structure

```text
gen-ai-tutor/
│
├── app.py                  # Main Streamlit application (UI, tabs, sidebar)
├── rag.py                  # RAG pipeline (PDF loading, chunking, FAISS, Gemini Q&A)
├── prompt.py               # Reusable prompt templates (CoT, Notes, Quiz, Summary, Study Plan)
├── roles.py                # Role-based system prompts (Teacher, Examiner, Coach, Expert)
├── examples.py             # Few-shot examples for structured answer formatting
├── study_chains.py         # LangChain LCEL Sequential Chain (Explanation → Notes → Quiz)
├── agent_tools.py          # LangChain Tool-Calling Agent with Calculator, Summarizer, Planner
├── profile_manager.py      # Student profile and learning history (JSON persistence)
├── ui_helpers.py           # CSS loader utility for theme switching
│
├── styles/
│   ├── dark.css            # Dark mode theme
│   └── light.css           # Light mode theme
│
├── data/                   # Uploaded and default PDF documents
│   └── computer_network.pdf
│
├── vector_db/              # Per-document FAISS indexes (auto-generated, gitignored)
│   └── <pdf_name>/
│       ├── index.faiss
│       └── index.pkl
│
├── screenshots/            # Project screenshots
├── user_profile.json       # Persistent student profile and learning history
├── requirements.txt        # Python dependencies
├── .env                    # API keys (not committed)
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/Sans-kriti5/gen-ai-tutor.git
cd gen-ai-tutor
```

### 2. Create a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure the API key
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

> Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 5. (Optional) Build the default vector database
```bash
python rag.py
```

This indexes `data/computer_network.pdf` into `vector_db/`.

### 6. Run the application
```bash
streamlit run app.py
```

---

## 🧠 Architecture

```
                         ┌─────────────────────────────────────┐
                         │         Streamlit Frontend           │
                         │  (app.py – Tabs, Sidebar, Chat UI)   │
                         └──────────────────┬──────────────────┘
                                            │
              ┌─────────────────────────────▼───────────────────────────────┐
              │                        RAG Pipeline (rag.py)                │
              │                                                             │
              │  PDF → PyPDF → Text Chunks → Gemini Embeddings → FAISS     │
              │                                                             │
              │  Query → FAISS Similarity Search → Context Retrieval       │
              │                                                             │
              │  Context + Role Prompt + CoT Prompt + History → Gemini     │
              └──────────────────────────────────────────────────────────────┘
                         │                             │
           ┌─────────────┘                 ┌───────────┘
           ▼                               ▼
  ┌─────────────────┐            ┌──────────────────────┐
  │  Sequential     │            │  Tool-Calling Agent   │
  │  LCEL Chain     │            │  (agent_tools.py)     │
  │  (study_chains) │            │                       │
  │                 │            │  ● Calculator         │
  │  Topic          │            │  ● Summarizer         │
  │    → Explain    │            │  ● Study Planner      │
  │    → Notes      │            └──────────────────────┘
  │    → Quiz       │
  └─────────────────┘
```

---

## 🔧 Known Issues & Limitations

### 🔴 Gemini Embedding Quota (Highest Priority)
The current embedding model (`GoogleGenerativeAIEmbeddings`) uses the **Gemini free tier quota**, which is exhausted quickly when indexing new documents.

**Planned Fix:** Replace with a **local embedding model** (e.g., `sentence-transformers/all-MiniLM-L6-v2`) via HuggingFace. This removes embedding quota dependency while continuing to use Gemini for reasoning.

```
PDF → Local Embedding Model → FAISS → Gemini 2.5 Flash (Reasoning)
```

### 🟡 `app.py` Size
The main application file has grown large and benefits from modular separation (sidebar, chat, tabs, state management).

---

## 🗺️ Future Roadmap

### 🔴 High Priority
- [ ] **Local Embeddings** — Replace `GoogleGenerativeAIEmbeddings` with `sentence-transformers` to eliminate API quota issues
- [ ] **Modular `app.py`** — Split into `sidebar.py`, `chat_ui.py`, `tabs.py`, `session_state.py`
- [ ] **Document Manager** — Show all indexed documents, switch between them without re-embedding

### 🟡 Medium Priority
- [ ] **Richer Learning History** — Store Role, Document Name, and Activity Type alongside topics
- [ ] **Statistics Dashboard** — Display Questions Asked, Documents Indexed, Study Time, Current Role
- [ ] **Settings Panel** — Allow configuration of Temperature, Retrieval Count (k), LLM model, Prompt style
- [ ] **Improved Chat UI** — Better avatars, typing indicators, message timestamps, cleaner chat bubbles
- [ ] **Error Handling** — Friendly messages for missing PDFs, corrupted indexes, quota exceeded, API failures

### 🟢 Nice to Have
- [ ] **Multi-language support** — Allow questions in different languages
- [ ] **Voice input** — Speech-to-text for questions
- [ ] **PDF Summarization** — One-click full document summary
- [ ] **Export Chat** — Download conversation history as PDF or Markdown
- [ ] **GIF/Screenshot documentation** — Add visual walkthrough to README

---

## 📊 Assignment Rubric Coverage

| # | Criterion | Status | Implementation |
|---|---|---|---|
| 1 | LLM API Integration | ✅ Complete | Gemini API, session chat history |
| 2 | Zero-Shot Prompting | ✅ Complete | `EXPLANATION_PROMPT`, `SUMMARY_PROMPT` |
| 3 | Few-Shot Prompting | ✅ Complete | `examples.py` injected into prompts |
| 4 | Chain-of-Thought | ✅ Complete | XML tag parsing, collapsible expander |
| 5 | Role Prompting | ✅ Complete | 4 roles, dynamic sidebar selection |
| 6 | Prompt Templates | ✅ Complete | Notes, Quiz, Summary, Study Plan templates |
| 7 | LangChain Chains | ✅ Complete | LCEL pipeline: Topic → Explanation → Notes → Quiz |
| 8 | Memory System | ✅ Complete | `user_profile.json`, history, personalization |
| 9 | Agents & Tools | ✅ Complete | Calculator, Summarizer, Study Planner tools |
| 10 | Final Integration | ✅ Complete | Full Streamlit app with all modules wired |

---

## 📸 Screenshots

> _Screenshots will be added to the `/screenshots` directory._

---

## 👩‍💻 Author

**Sanskriti Khatri**

Computer Engineering Student passionate about Artificial Intelligence, UI/UX Design, and Software Development.

[![GitHub](https://img.shields.io/badge/GitHub-Sans--kriti5-black?logo=github)](https://github.com/Sans-kriti5)

---

## 📄 License

This project is built for academic purposes as part of a Generative AI lab course.

---

*Made with ❤️ using Streamlit + Google Gemini + LangChain*