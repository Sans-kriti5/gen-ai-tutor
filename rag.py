import os
from dotenv import load_dotenv

from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI
)
from langchain_community.vectorstores import FAISS

from roles import ROLES
from examples import FEW_SHOT_EXAMPLES
from prompt import (
    COT_PROMPT,
    NOTE_PROMPT,
    SUMMARY_PROMPT,
    QUIZ_PROMPT,
    STUDY_PLAN_PROMPT
)

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

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text


# -------------------------------------------------------
# Split Text
# -------------------------------------------------------

def split_text(text):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)


# -------------------------------------------------------
# Create Vector Database
# -------------------------------------------------------

def create_vector_database(chunks):

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
# Load Vector Database
# -------------------------------------------------------

def load_vector_database():

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    return FAISS.load_local(
        "vector_db",
        embeddings,
        allow_dangerous_deserialization=True
    )


# -------------------------------------------------------
# Cached Vector Database Load (For Streamlit performance)
# -------------------------------------------------------

def load_cached_vector_db(file_name):
    """
    Caches the FAISS index database using Streamlit's cache_resource
    to avoid reading from disk on every rerun. Has fallback for scripts.
    """
    try:
        import streamlit as st
        @st.cache_resource
        def _load(name):
            return load_vector_database()
        return _load(file_name)
    except Exception:
        return load_vector_database()


# -------------------------------------------------------
# Retrieve Documents
# -------------------------------------------------------

def retrieve_documents(question, file_name="computer_network.pdf", k=3):

    vector_db = load_cached_vector_db(file_name)

    return vector_db.similarity_search(
        question,
        k=k
    )


# -------------------------------------------------------
# Ask Gemini (RAG with Memory)
# -------------------------------------------------------

def ask_gemini(question, role="Teacher", history=[], file_name="computer_network.pdf"):

    documents = retrieve_documents(question, file_name=file_name)

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    role_prompt = ROLES.get(
        role,
        ROLES["Teacher"]
    )

    cot_prompt = COT_PROMPT.format(
        context=context,
        question=question
    )

    # Format history if present
    history_str = ""
    if history:
        history_str = "\n".join(
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in history
        )
        history_section = f"""
--------------------------------------------------

Here is the conversation history so far:

{history_str}
"""
    else:
        history_section = ""

    prompt = f"""
{role_prompt}

--------------------------------------------------

Below are examples of how answers should be structured.

{FEW_SHOT_EXAMPLES}
{history_section}
--------------------------------------------------

Now answer the user's question.

{cot_prompt}

Rules:

- Answer ONLY using the provided context.
- If the answer is unavailable, reply:
"I couldn't find that information in the provided document."

Context:

{context}

Question:

{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content


# -------------------------------------------------------
# Direct Gemini Call
# -------------------------------------------------------

def generate_content(prompt):

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    response = llm.invoke(prompt)

    return response.content


# -------------------------------------------------------
# Study Tools Content Generator
# -------------------------------------------------------

def generate_study_tool_content(topic, mode="notes", file_name="computer_network.pdf"):
    """
    Retrieves documents relevant to the topic, formats them with the specified study tool prompt,
    and returns the model's response.
    Modes: "notes", "summary", "quiz", "study_plan"
    """
    documents = retrieve_documents(topic, file_name=file_name)
    context = "\n\n".join(doc.page_content for doc in documents)
    
    if not context.strip():
        return "I couldn't find enough information in the document to generate content for this topic."
        
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4
    )
    
    if mode == "notes":
        prompt = NOTE_PROMPT.format(context=context)
    elif mode == "summary":
        prompt = SUMMARY_PROMPT.format(context=context)
    elif mode == "quiz":
        prompt = QUIZ_PROMPT.format(context=context)
    elif mode == "study_plan":
        prompt = STUDY_PLAN_PROMPT.format(context=context)
    else:
        return "Invalid study tool mode."
        
    response = llm.invoke(prompt)
    return response.content


# -------------------------------------------------------
# Build RAG
# -------------------------------------------------------

def build_rag(pdf_path):

    text = load_pdf(pdf_path)

    chunks = split_text(text)

    create_vector_database(chunks)

    return True


# -------------------------------------------------------
# Terminal Testing
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print(" AI Academic Tutor - RAG Builder ")
    print("=" * 60)

    pdf_path = "data/computer_network.pdf"

    print("\nLoading PDF...")

    build_rag(pdf_path)

    print("\n✓ Vector Database Created Successfully!")

    print("\nRun:")

    print("streamlit run app.py")