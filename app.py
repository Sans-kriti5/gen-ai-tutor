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

    st.markdown("### 📄 Current Document")

    st.info("computer_network.pdf")

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

st.caption("Ask questions from your PDF using RAG + Gemini")

st.markdown("---")

# ---------------------------------
# Welcome Message
# ---------------------------------

if len(st.session_state.messages) == 0:

    with st.chat_message("assistant"):

        st.markdown(
            f"""
Hello 👋

I'm your **{st.session_state.role}** AI Tutor.

I can answer questions from your uploaded **Computer Network PDF**.

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

# ---------------------------------
# Chat Input
# ---------------------------------

question = st.chat_input(
    "Ask anything about Computer Networks..."
)

if question:

    # Save User Message

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # Assistant Response

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_gemini(
                question,
                st.session_state.role
            )

        st.markdown(answer)

    # Save Assistant Response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )