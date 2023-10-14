import streamlit as st
import streamlit_extras.app_logo as app_logo

def page_header():
    st.set_page_config(page_title="ComfyFlowApp: Load a comfyui workflow as webapp in seconds.", page_icon=":artist:", layout="wide")

    app_logo.add_logo("public/images/logo.png", height=70)

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
    
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) 