import os
import streamlit as st
from rag import ask_gemini
from ui_helpers import load_css

# ---------------------------------
# Page Configuration
# ---------------------------------

st.set_page_config(
    page_title="AI Academic Tutor",
    page_icon="📚",
    layout="wide"
)

# ---------------------------------
# Session State
# ---------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "role" not in st.session_state:
    st.session_state.role = "Teacher"

# Load Theme
load_css(st.session_state.theme)

# ---------------------------------
# Sidebar
# ---------------------------------

with st.sidebar:

    st.title("📚 AI Academic Tutor")

    st.markdown("---")

    st.markdown("### 🤖 Powered By")

    st.success("Google Gemini")
    st.success("Retrieval Augmented Generation (RAG)")
    st.success("FAISS Vector Database")
    st.success("LangChain")

    st.markdown("---")

    st.markdown("### 📄 Study Document")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Upload a PDF study material to query."
    )

    if uploaded_file is not None:
        from rag import build_rag
        
        save_dir = "data"
        os.makedirs(save_dir, exist_ok=True)
        pdf_path = os.path.join(save_dir, uploaded_file.name)
        
        if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
            with st.spinner(f"Reading and indexing {uploaded_file.name}..."):
                with open(pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                build_rag(pdf_path)
                st.session_state.current_file = uploaded_file.name
                st.session_state.messages = []
                st.success(f"Loaded {uploaded_file.name}!")
                st.rerun()
        
        st.info(f"Active: {uploaded_file.name}")
    else:
        if "current_file" in st.session_state and st.session_state.current_file != "computer_network.pdf":
            st.session_state.current_file = "computer_network.pdf"
            st.session_state.messages = []
            default_pdf = "data/computer_network.pdf"
            if not os.path.exists("vector_db") and os.path.exists(default_pdf):
                from rag import build_rag
                with st.spinner("Building default index..."):
                    build_rag(default_pdf)
            st.rerun()
        st.info("Active: computer_network.pdf")

    st.markdown("---")

    # -----------------------------
    # AI Role Selection
    # -----------------------------

    st.markdown("### 🎭 AI Role")

    st.session_state.role = st.selectbox(
        "Choose Assistant Role",
        [
            "Teacher",
            "Examiner",
            "Study Coach",
            "Subject Expert"
        ]
    )

    st.markdown("---")

    # -----------------------------
    # Personal Profile & Learning History
    # -----------------------------
    from profile_manager import load_profile, save_profile
    
    user_profile = load_profile()
    
    st.markdown("### 🎓 Personal Profile")
    profile_name = st.text_input("Name", value=user_profile.get("name", ""), placeholder="e.g. Sanskriti")
    profile_roll = st.text_input("Roll Number", value=user_profile.get("roll_number", ""), placeholder="e.g. 12")
    profile_dept = st.text_input("Department", value=user_profile.get("department", ""), placeholder="e.g. Computer Eng.")
    
    if st.button("💾 Save Profile"):
        user_profile["name"] = profile_name
        user_profile["roll_number"] = profile_roll
        user_profile["department"] = profile_dept
        save_profile(user_profile)
        st.success("Profile updated!")
        st.rerun()

    if user_profile["learning_history"]:
        st.markdown("### ⏳ Learning History")
        # Display the last 5 activities
        for entry in reversed(user_profile["learning_history"][-5:]):
            st.caption(f"📅 {entry['timestamp']}")
            st.markdown(f"**{entry['activity_type']}**: {entry['topic']}")
            st.markdown("---")

    st.markdown("---")

    # -----------------------------
    # Theme Toggle
    # -----------------------------

    st.markdown("### 🌙 Theme")

    light_mode = st.toggle(
        "Light Mode",
        value=(st.session_state.theme == "light")
    )

    new_theme = "light" if light_mode else "dark"

    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

    # -----------------------------
    # Clear Chat
    # -----------------------------

    if st.button("🗑 Clear Conversation"):

        st.session_state.messages = []

        st.rerun()

    st.markdown("---")

    st.caption("Made with ❤️ using Streamlit + Gemini")

# ---------------------------------
# Main Page
# ---------------------------------

st.title("📚 AI Academic Tutor")

st.caption("Ask questions and generate learning aids from your PDF using RAG + Gemini")

st.markdown("---")

# Create Tabs for different study features
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "💬 Chat Q&A", 
    "📝 Revision Notes", 
    "⚡ Quick Quiz", 
    "📅 Study Planner", 
    "📄 Summarizer",
    "🔗 Sequential Chain",
    "🤖 Agent Assistant"
])

with tab1:
    # ---------------------------------
    # Welcome Message
    # ---------------------------------
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            current_doc = st.session_state.get('current_file', 'computer_network.pdf')
            from profile_manager import load_profile
            user_profile = load_profile()
            student_name = user_profile.get("name", "").strip()
            greeting_name = f" {student_name}" if student_name else ""
            st.markdown(
                f"""
Hello{greeting_name} 👋

I'm your **{st.session_state.role}** AI Tutor.

I can answer questions from your uploaded **{current_doc}**.

### 💡 Try asking:
- What is Computer Network?
- Explain LAN.
- Difference between Hub and Switch.
- Explain OSI Model.
- What is TCP/IP?

Current Role:
**{st.session_state.role}**
"""
            )

    # ---------------------------------
    # Display Chat History
    # ---------------------------------
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "reasoning" in message and message["reasoning"]:
                with st.expander("🔍 Chain-of-Thought (Reasoning Steps)"):
                    st.markdown(message["reasoning"])
            st.markdown(message["content"])

with tab2:
    st.header("📝 Revision Notes Generator")
    st.write("Generate detailed, structured revision notes for any topic in the document.")
    note_topic = st.text_input("Enter Topic for Notes:", placeholder="e.g., OSI Model Layers", key="note_input")
    if st.button("Generate Notes 📝", key="note_btn"):
        if note_topic:
            with st.spinner("Generating revision notes..."):
                from rag import generate_study_tool_content
                notes = generate_study_tool_content(
                    note_topic, 
                    mode="notes", 
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
                st.markdown(notes)
        else:
            st.warning("Please enter a topic.")

with tab3:
    st.header("⚡ Quick Quiz Generator")
    st.write("Test your understanding with 5 custom multiple-choice questions on any topic.")
    quiz_topic = st.text_input("Enter Topic for Quiz:", placeholder="e.g., TCP vs UDP", key="quiz_input")
    if st.button("Generate Quiz ⚡", key="quiz_btn"):
        if quiz_topic:
            with st.spinner("Generating quiz..."):
                from rag import generate_study_tool_content
                quiz = generate_study_tool_content(
                    quiz_topic, 
                    mode="quiz", 
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
                st.markdown(quiz)
        else:
            st.warning("Please enter a topic.")

with tab4:
    st.header("📅 Study Planner")
    st.write("Get a step-by-step custom learning plan and self-test checklist for a topic.")
    plan_topic = st.text_input("Enter Topic for Study Plan:", placeholder="e.g., Routing Algorithms", key="plan_input")
    if st.button("Create Study Plan 📅", key="plan_btn"):
        if plan_topic:
            with st.spinner("Creating study plan..."):
                from rag import generate_study_tool_content
                plan = generate_study_tool_content(
                    plan_topic, 
                    mode="study_plan", 
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
                st.markdown(plan)
        else:
            st.warning("Please enter a topic.")

with tab5:
    st.header("📄 Section Summarizer")
    st.write("Summarize complex topics into a concise 150-word overview.")
    sum_topic = st.text_input("Enter Topic to Summarize:", placeholder="e.g., Hubs, Switches, and Routers", key="sum_input")
    if st.button("Generate Summary 📄", key="sum_btn"):
        if sum_topic:
            with st.spinner("Generating summary..."):
                from rag import generate_study_tool_content
                summary = generate_study_tool_content(
                    sum_topic, 
                    mode="summary", 
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
                st.markdown(summary)
        else:
            st.warning("Please enter a topic.")

with tab6:
    st.header("🔗 LangChain Sequential Chain Workflow")
    st.write("Execute a modular sequential pipeline: **Topic → Detailed Explanation → Revision Notes → Practice Quiz**.")
    st.info("The output of each step is passed as an input to the prompt for the next step.")
    
    seq_topic = st.text_input("Enter Topic for Sequential Study Flow:", placeholder="e.g. Subnetting", key="seq_topic_input")
    if st.button("Run Sequential Study Chain 🚀", key="seq_btn"):
        if seq_topic:
            with st.spinner("Executing LangChain Sequential pipeline..."):
                from study_chains import run_sequential_study_flow
                from profile_manager import add_to_learning_history
                
                # Log in history
                add_to_learning_history(seq_topic, "Sequential Chain")
                
                results = run_sequential_study_flow(
                    seq_topic,
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
                
                st.success("Workflow executed successfully!")
                st.markdown("### 💡 Step 1: Detailed Concept Explanation")
                st.markdown(results["explanation"])
                st.markdown("---")
                st.markdown("### 📝 Step 2: Generated Revision Notes")
                st.markdown(results["notes"])
                st.markdown("---")
                st.markdown("### ⚡ Step 3: Conceptual Practice Quiz")
                st.markdown(results["quiz"])
        else:
            st.warning("Please enter a topic.")

with tab7:
    st.header("🤖 LangChain Tool-Calling Agent")
    st.write("Interact with an AI Agent that automatically selects utility tools (Calculator, Summarizer, Planner) to answer queries.")
    
    agent_query = st.text_area(
        "Ask the agent a question:",
        placeholder="e.g. 'Calculate 1500 * 8 / (10**6) seconds transmission delay' OR 'Create a 5-day plan to learn Routing Algorithms'",
        key="agent_query_input"
    )
    
    if st.button("Ask Agent 🧠", key="agent_btn"):
        if agent_query:
            with st.spinner("Agent is reasoning and selecting tools..."):
                from agent_tools import run_agent_query
                from profile_manager import add_to_learning_history
                
                # Log in history
                add_to_learning_history(agent_query[:50], "Agent Q&A")
                
                agent_response = run_agent_query(agent_query)
                st.markdown("### 🤖 Agent Response:")
                st.markdown(agent_response)
        else:
            st.warning("Please enter a query.")

# ---------------------------------
# Chat Input (Always displayed at the bottom for Chat Q&A)
# ---------------------------------
current_doc = st.session_state.get('current_file', 'computer_network.pdf')
question = st.chat_input(
    f"Ask anything about {current_doc}..."
)

if question:
    # Save User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with tab1:
        with st.chat_message("user"):
            st.markdown(question)

        # Assistant Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response_dict = ask_gemini(
                    question,
                    st.session_state.role,
                    history=st.session_state.messages[:-1],
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
                answer = response_dict["answer"]
                reasoning = response_dict["reasoning"]
                
            if reasoning:
                with st.expander("🔍 Chain-of-Thought (Reasoning Steps)"):
                    st.markdown(reasoning)
            st.markdown(answer)

    # Save Assistant Response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "reasoning": reasoning
        }
    )