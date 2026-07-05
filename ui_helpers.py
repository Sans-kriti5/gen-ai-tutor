import streamlit as st


def load_css(theme="dark"):
    if theme == "dark":
        background = "#0E1117"
        sidebar = "#111827"
        text = "#FAFAFA"
        assistant_bg = "#1E293B"
    else:
        background = "#FFFFFF"
        sidebar = "#F3F4F6"
        text = "#111827"
        assistant_bg = "#F9FAFB"

    st.markdown(f"""
    <style>

    .stApp {{
        background-color: {background};
        color: {text};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sidebar};
    }}

    /* User bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
        border-left: 5px solid #22C55E;
        background-color: #143D21;
        border-radius: 15px;
        padding: 12px;
    }}

    /* Assistant bubble */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
        border-left: 5px solid #64748B;
        background-color: {assistant_bg};
        border-radius: 15px;
        padding: 12px;
    }}



    /* Buttons */
    .stButton>button {{
        background-color: #16a34a;
        color: white;
        border-radius: 10px;
        border: none;
    }}

    .stButton>button:hover {{
        background-color: #16A34A;
    }}

    </style>
    """, unsafe_allow_html=True)