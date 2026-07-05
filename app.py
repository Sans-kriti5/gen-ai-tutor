import streamlit as st
from rag import ask_gemini
from prompt import NOTE_PROMPT
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

# Load the CSS once
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

    st.markdown("### 🌙 Theme")

    light_mode = st.toggle(
        "Light Mode",
        value=(st.session_state.theme == "light")
    )

    # Determine the selected theme
    new_theme = "light" if light_mode else "dark"

    # Only rerun if the theme changed
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        st.rerun()

    st.markdown("---")

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
            """
Hello 👋

I'm your **AI Academic Tutor**.

I can answer questions from your uploaded **Computer Network PDF**.

### 💡 Try asking:

- What is Computer Network?
- Explain LAN.
- Difference between Hub and Switch.
- Explain OSI Model.
- What is TCP/IP?
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

    # AI Response

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_gemini(question)

        st.markdown(answer)

    # Save AI Response

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )