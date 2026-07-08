import os
from dotenv import load_dotenv

from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings,
    ChatGoogleGenerativeAI,
)
from langchain_community.vectorstores import FAISS

from roles import ROLES
from examples import FEW_SHOT_EXAMPLES
from prompt import (
    COT_PROMPT,
    NOTE_PROMPT,
    SUMMARY_PROMPT,
    QUIZ_PROMPT,
    STUDY_PLAN_PROMPT,
)

# -------------------------------------------------------
# Environment
# -------------------------------------------------------

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

EMBEDDING_MODEL = "models/gemini-embedding-001"

VECTOR_DB_DIR = "vector_db"


# -------------------------------------------------------
# PDF Reader
# -------------------------------------------------------

def load_pdf(pdf_path):
    """
    Read all text from a PDF.
    """

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
    """
    Split PDF into overlapping chunks.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_text(text)


# -------------------------------------------------------
# Utility Functions
# -------------------------------------------------------

def get_vector_db_path(file_name):
    """
    Convert:

        computer_network.pdf

    into

        vector_db/computer_network
    """

    pdf_name = os.path.splitext(
        os.path.basename(file_name)
    )[0]

    return os.path.join(
        VECTOR_DB_DIR,
        pdf_name
    )


# -------------------------------------------------------
# Create Vector Database
# -------------------------------------------------------

def create_vector_database(chunks, file_name):
    """
    Create FAISS index for one PDF.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    vector_db = FAISS.from_texts(
        chunks,
        embedding=embeddings
    )

    db_path = get_vector_db_path(file_name)

    os.makedirs(db_path, exist_ok=True)

    vector_db.save_local(db_path)

    return vector_db


# -------------------------------------------------------
# Load Vector Database
# -------------------------------------------------------

def load_vector_database(file_name):
    """
    Load the FAISS index of the selected PDF.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL
    )

    db_path = get_vector_db_path(file_name)

    return FAISS.load_local(
        db_path,
        embeddings,
        allow_dangerous_deserialization=True
    )


# -------------------------------------------------------
# Cached Database Loader
# -------------------------------------------------------

def load_cached_vector_db(file_name):
    """
    Cache loaded FAISS databases so Streamlit
    doesn't reload them on every rerun.
    """

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

def retrieve_documents(
    question,
    file_name="computer_network.pdf",
    k=3
):
    """
    Retrieve the most relevant chunks.
    """

    vector_db = load_cached_vector_db(file_name)

    return vector_db.similarity_search(
        question,
        k=k
    )

# -------------------------------------------------------
# Ask Gemini (RAG with Memory)
# -------------------------------------------------------

def ask_gemini(
    question,
    role="Teacher",
    history=None,
    file_name="computer_network.pdf"
):
    """
    Main RAG Question Answering Function.
    """

    if history is None:
        history = []

    # -----------------------------
    # Retrieve Context
    # -----------------------------

    documents = retrieve_documents(
        question,
        file_name=file_name
    )

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    # -----------------------------
    # Load LLM
    # -----------------------------

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    # -----------------------------
    # User Profile
    # -----------------------------

    from profile_manager import (
        get_personalization_prompt,
        add_to_learning_history
    )

    add_to_learning_history(
        question[:50],
        "Chat Q&A"
    )

    personalization = get_personalization_prompt()

    role_prompt = (
        personalization
        + ROLES.get(
            role,
            ROLES["Teacher"]
        )
    )

    # -----------------------------
    # Conversation History
    # -----------------------------

    history_section = ""

    if history:

        history_text = "\n".join(

            f"{'User' if msg['role']=='user' else 'Assistant'}: {msg['content']}"

            for msg in history
        )

        history_section = f"""

--------------------------------------------------

Conversation History

{history_text}

"""

    # -----------------------------
    # Chain of Thought Prompt
    # -----------------------------

    cot_prompt = COT_PROMPT.format(

        context=context,

        question=question

    )

    # -----------------------------
    # Final Prompt
    # -----------------------------

    prompt = f"""

{role_prompt}

--------------------------------------------------

Below are examples of ideal answers.

{FEW_SHOT_EXAMPLES}

{history_section}

--------------------------------------------------

Now answer the user's question.

{cot_prompt}

Rules:

• Use ONLY the provided context.

• If the answer is unavailable, reply exactly:

"I couldn't find that information in the provided document."

Context:

{context}

Question:

{question}

Answer:

"""

    # -----------------------------
    # Call Gemini
    # -----------------------------

    response = llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):

        parts = []

        for item in content:

            if isinstance(item, dict):

                if "text" in item:

                    parts.append(item["text"])

            elif isinstance(item, str):

                parts.append(item)

        content = "".join(parts)

    elif not isinstance(content, str):

        content = str(content)

    # -----------------------------
    # Parse XML Tags
    # -----------------------------

    import re

    reasoning_match = re.search(

        r"<reasoning_chain>(.*?)</reasoning_chain>",

        content,

        re.DOTALL

    )

    answer_match = re.search(

        r"<answer>(.*?)</answer>",

        content,

        re.DOTALL

    )

    reasoning = ""

    answer = content.strip()

    if reasoning_match:

        reasoning = reasoning_match.group(1).strip()

    if answer_match:

        answer = answer_match.group(1).strip()

    if not answer_match:

        answer = re.sub(

            r"</?(reasoning_chain|answer)>",

            "",

            answer

        ).strip()

    return {

        "reasoning": reasoning,

        "answer": answer

    }


# -------------------------------------------------------
# Direct Gemini Prompt
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

def generate_study_tool_content(
    topic,
    mode="notes",
    file_name="computer_network.pdf"
):
    """
    Generate revision notes, summaries, quizzes,
    or study plans using the indexed PDF.
    """

    documents = retrieve_documents(
        topic,
        file_name=file_name
    )

    context = "\n\n".join(
        doc.page_content
        for doc in documents
    )

    if not context.strip():

        return (
            "I couldn't find enough information "
            "in the document."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4
    )

    if mode == "notes":

        prompt = NOTE_PROMPT.format(
            context=context
        )

    elif mode == "summary":

        prompt = SUMMARY_PROMPT.format(
            context=context
        )

    elif mode == "quiz":

        prompt = QUIZ_PROMPT.format(
            context=context
        )

    elif mode == "study_plan":

        prompt = STUDY_PLAN_PROMPT.format(
            context=context
        )

    else:

        return "Invalid study tool mode."

    response = llm.invoke(prompt)

    return response.content


# -------------------------------------------------------
# Build RAG
# -------------------------------------------------------

def build_rag(pdf_path):
    """
    Build the vector database only if it
    doesn't already exist.
    """

    pdf_name = os.path.basename(pdf_path)

    db_path = get_vector_db_path(pdf_name)

    faiss_file = os.path.join(
        db_path,
        "index.faiss"
    )

    pkl_file = os.path.join(
        db_path,
        "index.pkl"
    )

    # Already Indexed
    if os.path.exists(faiss_file) and os.path.exists(pkl_file):

        print(f"✓ {pdf_name} already indexed.")

        return True

    print(f"\nCreating embeddings for {pdf_name}...")

    text = load_pdf(pdf_path)

    chunks = split_text(text)

    create_vector_database(
        chunks,
        pdf_name
    )

    print("✓ Vector database created.")

    return True


# -------------------------------------------------------
# Build Every PDF in data/
# -------------------------------------------------------

def build_all_documents():
    """
    Index every PDF inside the data folder.
    Existing indexes are skipped.
    """

    data_folder = "data"

    if not os.path.exists(data_folder):

        print("Data folder not found.")

        return

    pdf_files = [

        file

        for file in os.listdir(data_folder)

        if file.lower().endswith(".pdf")

    ]

    if not pdf_files:

        print("No PDF files found.")

        return

    print("\nFound PDFs:")

    for pdf in pdf_files:

        print(" •", pdf)

    print()

    for pdf in pdf_files:

        build_rag(

            os.path.join(
                data_folder,
                pdf
            )

        )


# -------------------------------------------------------
# Terminal Testing
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print(" AI Academic Tutor ")
    print("=" * 60)

    build_all_documents()

    print("\nEverything is ready!")

    print("\nRun the application using:\n")

    print("streamlit run app.py")