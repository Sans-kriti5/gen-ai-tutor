import os
import streamlit as st

from rag import ask_gemini, build_rag
from prompt import (
    NOTE_PROMPT,
    SUMMARY_PROMPT,
    QUIZ_PROMPT
)

from ui_helpers import load_css

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------

st.set_page_config(
    page_title="AI Academic Tutor",
    page_icon="📚",
    layout="wide"
)

# ----------------------------------------------------
# SESSION STATE
# ----------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "pdf_ready" not in st.session_state:
    st.session_state.pdf_ready = False

if "current_pdf" not in st.session_state:
    st.session_state.current_pdf = None

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

load_css(st.session_state.theme)

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------

with st.sidebar:

    st.title("📚 AI Academic Tutor")

    st.markdown("---")

    st.markdown("## 📂 Upload PDF")

    uploaded_pdf = st.file_uploader(
        "Choose a PDF",
        type=["pdf"]
    )

    if uploaded_pdf is not None:

        os.makedirs("data", exist_ok=True)

        save_path = os.path.join(
            "data",
            uploaded_pdf.name
        )

        with open(save_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())

        if st.session_state.current_pdf != uploaded_pdf.name:

            with st.spinner("Creating Vector Database..."):

                build_rag(save_path)

            st.session_state.pdf_ready = True
            st.session_state.current_pdf = uploaded_pdf.name

            st.success("PDF Indexed Successfully!")

    st.markdown("---")

    st.markdown("### 📄 Current PDF")

    if st.session_state.current_pdf:

        st.success(st.session_state.current_pdf)

    else:

        st.warning("No PDF Uploaded")

    st.markdown("---")

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

    st.markdown("### 🤖 Technology")

    st.success("Google Gemini")
    st.success("RAG")
    st.success("FAISS")
    st.success("LangChain")

    st.markdown("---")

    if st.button("🗑 Clear Conversation"):

        st.session_state.messages = []
        st.session_state.last_answer = ""

        st.rerun()

    st.markdown("---")

    st.caption("Made with ❤️ using Streamlit + Gemini")

# ----------------------------------------------------
# MAIN PAGE
# ----------------------------------------------------

st.title("📚 AI Academic Tutor")

st.caption(
    "Upload your study material and chat with it."
)

st.markdown("---")

# ----------------------------------------------------
# WELCOME SCREEN
# ----------------------------------------------------

if not st.session_state.pdf_ready:

    st.info("👈 Upload a PDF from the sidebar to begin.")

    st.stop()

if len(st.session_state.messages) == 0:

    with st.chat_message("assistant"):

        st.markdown(
            """
# 👋 Welcome!

I'm your AI Academic Tutor.

After uploading a PDF I can help you with:

- 📚 Explain Concepts
- 📝 Summarize Chapters
- 🧠 Generate MCQs
- 📖 Create Revision Notes
- 💡 Answer Questions

Start by asking any question below.
"""
        )
# ----------------------------------------------------
# DISPLAY CHAT HISTORY
# ----------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ----------------------------------------------------
# CHAT INPUT
# ----------------------------------------------------

question = st.chat_input(
    "Ask anything about your uploaded PDF..."
)

if question:

    # -----------------------------
    # User Message
    # -----------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)

    # -----------------------------
    # Assistant Response
    # -----------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_gemini(question)

        st.markdown(answer)

    # Save Answer

    st.session_state.last_answer = answer

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# ----------------------------------------------------
# EXTRA AI FEATURES
# ----------------------------------------------------

if st.session_state.last_answer != "":

    st.markdown("---")

    st.subheader("✨ AI Learning Tools")

    col1, col2, col3 = st.columns(3)

    # ============================================
    # Generate Notes
    # ============================================

    with col1:

        if st.button("📚 Generate Notes"):

            with st.spinner("Generating Notes..."):

                notes_prompt = NOTE_PROMPT.format(
                    context=st.session_state.last_answer
                )

                notes = ask_gemini(notes_prompt)

            st.markdown("### 📚 Revision Notes")

            st.success(notes)

    # ============================================
    # Summary
    # ============================================

    with col2:

        if st.button("📝 Summarize Chapter"):

            with st.spinner("Summarizing..."):

                summary_prompt = SUMMARY_PROMPT.format(
                    context=st.session_state.last_answer
                )

                summary = ask_gemini(summary_prompt)

            st.markdown("### 📝 Summary")

            st.info(summary)

    # ============================================
    # Quiz
    # ============================================

    with col3:

        if st.button("🧠 Quiz Me"):

            with st.spinner("Creating Quiz..."):

                quiz_prompt = QUIZ_PROMPT.format(
                    context=st.session_state.last_answer
                )

                quiz = ask_gemini(quiz_prompt)

            st.markdown("### 🧠 Quiz")

            st.warning(quiz)

# ----------------------------------------------------
# DOWNLOAD ANSWER
# ----------------------------------------------------

if st.session_state.last_answer != "":

    st.download_button(

        label="⬇ Download Last Answer",

        data=st.session_state.last_answer,

        file_name="answer.txt",

        mime="text/plain"
    )

# ----------------------------------------------------
# FOOTER
# ----------------------------------------------------

st.markdown("---")

st.caption(
    "🚀 AI Academic Tutor | Built with Streamlit, Gemini & RAG"
)