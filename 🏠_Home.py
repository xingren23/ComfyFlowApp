import argparse
from loguru import logger

import streamlit as st
import streamlit_extras.app_logo as app_logo

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--server_addr", type=str, default="127.0.0.1:8188")
    try:
        args = parser.parse_args()
        server_addr = args.server_addr

        st.set_page_config(page_title="ComfyFlowApp", layout="wide")

        st.session_state['server_addr'] = server_addr
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
        with open("public/home.md", "r") as f:
            text = f.read()
            st.markdown(text)

    except SystemExit as e:
        logger.error(e)
        exit()
