import os
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load API Key
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


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


def split_text(text):
    """
    Splits text into smaller chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_text(text)

    return chunks


def create_vector_database(chunks):
    """
    Creates embeddings and stores them inside FAISS.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview"
    )

    vector_db = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    vector_db.save_local("vector_db")

    return vector_db
def load_vector_database():
    """
    Loads the saved FAISS vector database.
    """

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-2-preview"
    )

    vector_db = FAISS.load_local(
        "vector_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_db


def retrieve_documents(question):
    """
    Returns the most relevant chunks for the given question.
    """

    vector_db = load_vector_database()

    documents = vector_db.similarity_search(
        question,
        k=5
    )

    return documents
def ask_gemini(question):
    """
    Retrieves relevant context and asks Gemini to answer.
    """

    documents = retrieve_documents(question)

    context = "\n\n".join([doc.page_content for doc in documents])

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    prompt = f"""
You are an AI Academic Tutor for Computer Engineering students.

Your job is to explain concepts clearly and in simple language.

Instructions:
- Answer ONLY using the provided context.
- Explain the concept in 5–10 sentences whenever possible.
- Include a definition.
- Explain important points.
- Use bullet points if appropriate.
- Do not invent information that is not in the context.

If the answer is not available in the context, reply:
"I couldn't find that information in the provided document."

======================
Context:
{context}
======================

Question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    return response.content

if __name__ == "__main__":
    print("RAG Module Loaded Successfully.")

    print("=" * 60)
    print(" AI Academic Tutor - RAG Builder ")
    print("=" * 60)

    pdf_path = "data/computer_network.pdf"

    print("\nLoading PDF...")
    text = load_pdf(pdf_path)
    print("✓ PDF Loaded")

    print(f"\nCharacters Extracted : {len(text)}")

    print("\nSplitting into Chunks...")
    chunks = split_text(text)
    print(f"✓ Total Chunks : {len(chunks)}")

    print("\nCreating Embeddings...")
    vector_db = create_vector_database(chunks)

    print("✓ Embeddings Created")
    print("✓ FAISS Database Saved")

print("\nRAG Setup Completed Successfully!")

