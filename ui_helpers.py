import streamlit as st


def load_css(theme="dark"):
    """
    Loads the CSS file based on the selected theme.
    """

    css_file = f"styles/{theme}.css"

    with open(css_file, "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True
    )