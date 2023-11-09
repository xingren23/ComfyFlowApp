from loguru import logger
import os
import streamlit as st
import streamlit_extras.app_logo as app_logo
from streamlit_extras.badges import badge
from streamlit_extras.stylable_container import stylable_container
from streamlit.source_util import (
    get_pages,
    _on_pages_changed,
    invalidate_pages_cache,
)

def change_mode_pages():
    if 'main_script_path' in st.session_state:
        main_script_path = st.session_state['main_script_path']
        mode = st.session_state['mode']
        invalidate_pages_cache()
        all_pages = get_pages(main_script_path)
        if mode == "Studio":
            pages = ['Home', 'My_Apps', "App_Store"]
        else:
            pages = [page['page_name'] for _, page in all_pages.items()]
        logger.info(f"pages: {pages}, mode: {mode}")

        current_pages = [key for key, value in all_pages.items() if value['page_name'] not in pages]
        for key in current_pages:
            all_pages.pop(key)
            
        _on_pages_changed.send()


def page_init(layout="wide"):
    """
    mode, studio or creator
    """
    st.set_page_config(page_title="ComfyFlowApp: Load a comfyui workflow as webapp in seconds.", 
    page_icon=":artist:", layout=layout)

    if 'main_script_path' not in st.session_state:
        st.session_state['main_script_path'] = os.path.abspath('../Home.py')
    if 'mode' not in st.session_state:
        logger.info("init mode to Studio")
        st.session_state['mode'] = "Studio"
        change_mode_pages()

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
        

        with exchange_button_container():
            new_mode = "Creator" if st.session_state['mode'] == "Studio" else "Studio"   
            
            st.markdown(f"Current Mode: {st.session_state['mode']} :smile:")
            exchange_button = st.button(f"Exchange To {new_mode}", key="exchange_button")
            if exchange_button:
                st.session_state['mode'] = new_mode
                change_mode_pages()
                st.rerun()

        st.sidebar.markdown("""
        <style>
        [data-testid='stSidebarNav'] > ul {
            min-height: 65vh;
        } 
        </style>
        """, unsafe_allow_html=True)

        badge(type="github", name="xingren23/ComfyFlowApp", url="https://github.com/xingren23/ComfyFlowApp")
        badge(type="twitter", name="xingren23", url="https://twitter.com/xingren23")
    

def stylable_button_container():
    return stylable_container(
        key="app_button",
        css_styles="""
            button {
                background-color: rgb(28 131 225);
                color: white;
                border-radius: 4px;
                width: 120px;
            }
            button:hover, button:focus {
                border: 0px solid rgb(28 131 225);
            }
        """,
    )

def exchange_button_container():
    return stylable_container(
        key="exchange_button",
        css_styles="""
            button {
                background-color: rgb(28 131 225);
                color: white;
                border-radius: 4px;
                width: 200px;
            }
            button:hover, button:focus {
                border: 0px solid rgb(28 131 225);
            }
        """,
    )

def custom_text_area():
    custom_css = """
            <style>
            textarea {
                height: auto;
                max-height: 250px;
            }
            </style>
        """
        # 将自定义CSS样式添加到Streamlit中
    st.markdown(custom_css, unsafe_allow_html=True)