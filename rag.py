import os
from dotenv import load_dotenv

from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from langchain_community.vectorstores import FAISS

# -------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# -------------------------------------------------------
# Embedding Model
# -------------------------------------------------------

EMBEDDING_MODEL = "models/gemini-embedding-001"

# -------------------------------------------------------
# Read PDF
# -------------------------------------------------------

def load_pdf(pdf_path):
    """
    Reads a PDF and returns all extracted text.
    """

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


# -------------------------------------------------------
# Split Text into Chunks
# -------------------------------------------------------

def split_text(text):
    """
    Splits the PDF text into overlapping chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    return chunks


# -------------------------------------------------------
# Create Vector Database
# -------------------------------------------------------

def create_vector_database(chunks):
    """
    Creates embeddings and stores them inside FAISS.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_db = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    vector_db.save_local("vector_db")

    return vector_db


# -------------------------------------------------------
# Load Existing Vector Database
# -------------------------------------------------------

def load_vector_database():
    """
    Loads the saved FAISS vector database.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_db = FAISS.load_local(
        "vector_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_db


# -------------------------------------------------------
# Retrieve Relevant Documents
# -------------------------------------------------------

def retrieve_documents(question, k=3):
    """
    Retrieves the most relevant chunks from FAISS.
    """

    vector_db = load_vector_database()

    docs = vector_db.similarity_search(
        question,
        k=k
    )

    return docs


# -------------------------------------------------------
# Ask Gemini
# -------------------------------------------------------

def ask_gemini(question):
    """
    Retrieves relevant context from FAISS and asks Gemini.
    """

    documents = retrieve_documents(question)

    context = "\n\n".join(
        [doc.page_content for doc in documents]
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    prompt = f"""
You are an AI Academic Tutor for Computer Engineering students.

Answer ONLY using the provided context.

Instructions:

- Explain concepts in simple language.
- Keep answers between 5 and 10 sentences.
- Use bullet points whenever suitable.
- If the answer isn't present in the context, say:

"I couldn't find that information in the provided document."

-------------------------
Context:

{context}

-------------------------

Question:

{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content
# -------------------------------------------------------
# Direct Gemini Call (No RAG)
# -------------------------------------------------------

def generate_content(prompt):
    """
    Sends a prompt directly to Gemini without retrieving context.
    Used for Notes, Summary, Quiz, etc.
    """

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    response = llm.invoke(prompt)

    return response.content


# -------------------------------------------------------
# Build Vector Database
# -------------------------------------------------------

def build_rag(pdf_path):
    """
    Complete RAG pipeline.
    """

    text = load_pdf(pdf_path)

    chunks = split_text(text)

    create_vector_database(chunks)

    return True


# -------------------------------------------------------
# Terminal Testing Only
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print(" AI Academic Tutor - RAG Builder ")
    print("=" * 60)

    pdf_path = "data/computer_network.pdf"

    print("\nLoading PDF...")

    build_rag(pdf_path)

    print("\n✓ Vector Database Created Successfully!")

    print("\nYou can now run:")

    print("streamlit run app.py")