# 📚 AI Academic Tutor

An AI-powered academic assistant built with **Google Gemini**, **LangChain**, and **Retrieval-Augmented Generation (RAG)**. The application enables students to ask questions from their study materials and receive context-aware answers using semantic search over PDF documents.

---

## 🚀 Features

- 📄 Ask questions from study materials
- 🤖 AI-powered responses using Google Gemini
- 🔍 Retrieval-Augmented Generation (RAG)
- ⚡ Semantic search using FAISS vector database
- 💬 Interactive chat interface built with Streamlit
- 🌙 Light and Dark theme support
- 🧹 Clear conversation history
- 📚 Context-aware answers from uploaded documents

---

## 🛠️ Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Frontend | Streamlit |
| LLM | Google Gemini |
| Framework | LangChain |
| Vector Database | FAISS |
| PDF Processing | PyPDF |
| Version Control | Git & GitHub |

---

## 📂 Project Structure

```text
gen-ai-tutor/
│
├── app.py                 # Streamlit application
├── rag.py                 # RAG pipeline
├── prompt.py              # Prompt templates
├── ui_helpers.py          # UI utilities
├── requirements.txt
├── .gitignore
├── README.md
│
├── data/
│   ├── computer_network.pdf
│   ├── CN-Chapter-1-2.pdf
│   └── CN-chapter-5.pdf
│
├── styles/
│   ├── dark.css
│   └── light.css
│
├── vector_db/
│
└── .streamlit/
    └── config.toml
```

---

## 🧠 How It Works

1. Load PDF documents.
2. Extract text from the PDFs.
3. Split the text into smaller chunks.
4. Generate embeddings using Google Gemini.
5. Store embeddings in a FAISS vector database.
6. Retrieve the most relevant chunks based on the user's query.
7. Generate a context-aware answer using Gemini.

---

## ⚙️ Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Sans-kriti5/gen-ai-tutor.git
cd gen-ai-tutor
```

### 2️⃣ Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create a `.env` file

```env
GOOGLE_API_KEY=your_api_key_here
```

### 5️⃣ Run the application

```bash
streamlit run app.py
```

---

## 📸 Screenshots

### Home Page

> *(Add screenshot here)*

### Chat Interface

> *(Add screenshot here)*

### Dark Mode

> *(Add screenshot here)*

---

## 🚀 Future Improvements

- 📂 Upload PDFs directly from the application
- 📚 Support multiple PDF documents
- 📄 Display source citations and page numbers
- 📝 AI-generated notes and summaries
- 🧠 Quiz generation from study materials
- 🌐 Multi-language support
- 🎤 Voice-based interaction

---

## 🤝 Contributing

Contributions are welcome!

If you'd like to improve the project:

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Open a Pull Request

---

## 👩‍💻 Author

**Sanskriti Khatri**

Computer Engineering Student | AI Enthusiast | UI/UX Designer

- GitHub: https://github.com/Sans-kriti5

---

## 📄 License

This project is intended for educational and learning purposes.