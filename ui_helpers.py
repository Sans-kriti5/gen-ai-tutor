import os
import streamlit as st


def load_css(theme="dark"):
    """
    Loads the CSS file based on the selected theme.
    """

    css_file = os.path.join("styles", f"{theme}.css")

    if not os.path.exists(css_file):
        st.error(f"CSS file not found: {css_file}")
        return

    with open(css_file, "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )