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
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Chat Q&A", 
    "📝 Revision Notes", 
    "⚡ Quick Quiz", 
    "📅 Study Planner", 
    "📄 Summarizer"
])

with tab1:
    # ---------------------------------
    # Welcome Message
    # ---------------------------------
    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            current_doc = st.session_state.get('current_file', 'computer_network.pdf')
            st.markdown(
                f"""
Hello 👋

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
                answer = ask_gemini(
                    question,
                    st.session_state.role,
                    history=st.session_state.messages[:-1],
                    file_name=st.session_state.get('current_file', 'computer_network.pdf')
                )
            st.markdown(answer)

    # Save Assistant Response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )