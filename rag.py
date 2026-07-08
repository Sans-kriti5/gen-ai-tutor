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
# -------------------------------------------------------
# Create Vector Database
# -------------------------------------------------------

def create_vector_database(chunks, db_path):

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_db = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    os.makedirs(db_path, exist_ok=True)

    vector_db.save_local(db_path)

    return vector_db

# -------------------------------------------------------
# Load Vector Database
# -------------------------------------------------------

def load_vector_database(file_name):

    pdf_name = os.path.splitext(file_name)[0]

    db_path = os.path.join(
        "vector_db",
        pdf_name
    )

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    return FAISS.load_local(
        db_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
# -------------------------------------------------------
# Cached Vector Database Load (For Streamlit performance)
# -------------------------------------------------------

def load_cached_vector_db(file_name):

    try:

        import streamlit as st

        @st.cache_resource
        def _load(name):

            return load_vector_database(name)

        return _load(file_name)

    except Exception:

        return load_vector_database(file_name)

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

    from profile_manager import get_personalization_prompt, add_to_learning_history
    
    # Track in history
    add_to_learning_history(question[:50], "Chat Q&A")

    personalization = get_personalization_prompt()
    role_prompt = personalization + ROLES.get(
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
    content = response.content
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
        content = "".join(text_parts)
    elif not isinstance(content, str):
        content = str(content)

    # Parse Chain-of-Thought XML tags
    import re
    reasoning_match = re.search(r'<reasoning_chain>(.*?)</reasoning_chain>', content, re.DOTALL)
    answer_match = re.search(r'<answer>(.*?)</answer>', content, re.DOTALL)
    
    reasoning = reasoning_match.group(1).strip() if reasoning_match else ""
    answer = answer_match.group(1).strip() if answer_match else content.strip()
    
    # Clean up tags if none matched but some exist
    if not answer_match and not reasoning_match:
        answer = re.sub(r'</?(reasoning_chain|answer)>', '', answer).strip()
        
    return {
        "reasoning": reasoning,
        "answer": answer
    }


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

    pdf_name = os.path.splitext(
        os.path.basename(pdf_path)
    )[0]

    db_path = os.path.join(
        "vector_db",
        pdf_name
    )

    # If already indexed, don't create embeddings again
    if os.path.exists(
        os.path.join(db_path, "index.faiss")
    ):
        print(f"{pdf_name} already indexed.")

        return True

    print(f"Creating vector database for {pdf_name}...")

    text = load_pdf(pdf_path)

    chunks = split_text(text)

    create_vector_database(
        chunks,
        db_path
    )

    print("Done.")

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