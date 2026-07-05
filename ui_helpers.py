import streamlit as st


def load_css(theme="dark"):
    css_path = f"styles/{theme}.css"

    with open(css_path, "r", encoding="utf-8") as css:
        st.markdown(
            f"<style>{css.read()}</style>",
            unsafe_allow_html=True,
        )