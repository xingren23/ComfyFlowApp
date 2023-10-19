import streamlit as st
import streamlit_extras.app_logo as app_logo
from streamlit_extras.badges import badge

def page_header():    
    st.set_page_config(page_title="ComfyFlowApp: Load a comfyui workflow as webapp in seconds.", 
    page_icon=":artist:", layout="wide")

    app_logo.add_logo("public/images/logo.png", height=70)

    # reduce top padding
    st.markdown("""
            <style>
                .block-container {
                        padding-top: 1rem;
                        padding-bottom: 0rem;
                        # padding-left: 5rem;
                        # padding-right: 5rem;
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

    with st.sidebar:    
        st.sidebar.markdown("""
        <style>
        [data-testid='stSidebarNav'] > ul {
            min-height: 70vh;
        } 
        </style>
        """, unsafe_allow_html=True)

        badge(type="github", name="xingren23/ComfyFlowApp", url="https://github.com/xingren23/ComfyFlowApp")
        badge(type="twitter", name="xingren23", url="https://twitter.com/xingren23")
    