from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from profile_manager import get_personalization_prompt
from rag import retrieve_documents

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

# --------------------------------------------------
# Chain Definitions (LCEL)
# --------------------------------------------------

# 1. Explanation Chain
explanation_prompt_tpl = PromptTemplate.from_template(
    "You are an academic tutor. {personalization}\n"
    "Explain the topic '{topic}' clearly in simple language using the provided study material context.\n\n"
    "Context:\n{context}\n\n"
    "Detailed Explanation:"
)
explanation_chain = explanation_prompt_tpl | llm | StrOutputParser()

# 2. Notes Chain
notes_prompt_tpl = PromptTemplate.from_template(
    "Convert the following academic explanation into concise, structured bullet-point revision notes with clear headings.\n\n"
    "Explanation:\n{context}\n\n"
    "Revision Notes:"
)
notes_chain = notes_prompt_tpl | llm | StrOutputParser()

# 3. Quiz Chain
quiz_prompt_tpl = PromptTemplate.from_template(
    "Generate exactly 3 multiple-choice questions to test understanding of these revision notes. "
    "For each question, provide options A, B, C, D and list the correct answer key with a brief explanation.\n\n"
    "Notes:\n{context}\n\n"
    "Quiz:"
)
quiz_chain = quiz_prompt_tpl | llm | StrOutputParser()

# --------------------------------------------------
# Sequential Execution Workflow
# --------------------------------------------------

def run_sequential_study_flow(topic, file_name="computer_network.pdf"):
    """
    Executes a sequential pipeline: Topic -> Explanation -> Notes -> Quiz.
    Outputs of each step are passed as inputs to the next.
    """
    # 1. Retrieve RAG Context
    docs = retrieve_documents(topic, file_name=file_name)
    context = "\n\n".join(doc.page_content for doc in docs)
    if not context.strip():
        context = "No specific study material context found. Please use standard academic knowledge."

    # 2. Get Student Personalization Prefix
    personalization = get_personalization_prompt()

    # Step 1: Generate Explanation
    explanation = explanation_chain.invoke({
        "personalization": personalization,
        "topic": topic,
        "context": context
    })

    # Step 2: Generate Notes from Explanation
    notes = notes_chain.invoke({
        "context": explanation
    })

    # Step 3: Generate Quiz from Notes
    quiz = quiz_chain.invoke({
        "context": notes
    })

    return {
        "explanation": explanation,
        "notes": notes,
        "quiz": quiz
    }
