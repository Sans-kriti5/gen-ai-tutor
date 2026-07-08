import re
from langchain_core.tools import tool
try:
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError:
    from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from profile_manager import get_personalization_prompt

# --------------------------------------------------
# Define Agent Tools
# --------------------------------------------------

@tool
def calculate_math(expression: str) -> str:
    """
    Useful for performing mathematical calculations. Input should be a valid mathematical expression (e.g. '10 * 1024 / 2.5' or '2**10').
    Returns the result of the calculation as a string.
    """
    expression = expression.strip()
    # Sanitize the expression to allow only numbers, basic arithmetic operators, parentheses, and spaces
    if not re.match(r'^[0-9+\-*/().%\s]+$', expression):
        return "Error: Invalid characters in math expression. Only digits and operators (+, -, *, /, **, %, (, )) are allowed."
    try:
        # Safe evaluation with limited builtins
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Error: Could not calculate math expression. {str(e)}"

@tool
def summarize_text(text: str, max_words: int = 100) -> str:
    """
    Summarizes a block of text into a specified maximum word length.
    Input parameters: 'text' (the string content to summarize), 'max_words' (integer representing the target maximum word count, default 100).
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    prompt = f"Please summarize the following academic text in under {max_words} words:\n\n{text}"
    response = llm.invoke(prompt)
    return response.content

@tool
def create_study_schedule(topic: str, duration_days: int = 7) -> str:
    """
    Generates a day-by-day learning schedule and roadmap for a given topic and number of days.
    Input parameters: 'topic' (the subject or concept to study), 'duration_days' (integer number of days for the plan, default 7).
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.4)
    prompt = (
        f"Create a day-by-day study schedule and learning roadmap for the topic '{topic}' over {duration_days} days. "
        "Include daily topics, study activities, and a quick self-test suggestion for the final day."
    )
    response = llm.invoke(prompt)
    return response.content

# --------------------------------------------------
# Define Agent Initialization & Execution
# --------------------------------------------------

tools = [calculate_math, summarize_text, create_study_schedule]

def run_agent_query(user_query):
    """
    Creates and executes a Tool-Calling Agent to solve user questions using calculators, summarizers, or planners.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
    
    # Load personalization context
    personalization = get_personalization_prompt()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful and intelligent AI Academic Tutor. {personalization}\n"
                   "You have access to tools: calculator, summarizer, and study planner. "
                   "If the user asks you to calculate something, summarize something, or plan something, call the corresponding tool. "
                   "Otherwise, answer their question directly using your academic knowledge. "
                   "Always be helpful, encouraging, and friendly."),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    response = agent_executor.invoke({"input": user_query})
    return response["output"]
