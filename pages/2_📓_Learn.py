
import streamlit as st
import streamlit_extras.app_logo as app_logo

st.set_page_config(page_title="ComfyFlowApp", layout="wide")

app_logo.add_logo("public/images/logo.png", height=50)

# reduce top padding
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

# read in the markdown file
with open("public/learn.md", "r") as f:
    text = f.read()
    st.markdown(text)
    