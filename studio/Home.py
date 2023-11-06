import streamlit as st
from streamlit_extras.row import row
from modules import page, get_auth_instance

page.page_init(layout="centered")

with st.container():
    header_row = row([0.85, 0.15], vertical_align="bottom")
    header_row.markdown("""
        ## Welcome to ComfyFlowApp
        Discover and install ai art apps from the store.
    """)
    emtpy_button = header_row.empty()
    auth_instance = get_auth_instance()
    if not st.session_state['authentication_status']:
        login_tab, reg_tab = st.tabs(["Login", "Register"])
        with login_tab:
            try:
                auth_instance.login("Login to ComfyFlowApp")
            except Exception as e:
                st.error(f"Login failed, {e}")
        with reg_tab:
            try:
                auth_instance.register_user("Register a new user of ComfyFlowApp", preauthorization=False)
            except Exception as e:
                st.error(f"Register failed, {e}")
    else: 
        with emtpy_button:
            auth_instance.logout("Logout")
        with st.container():
            name = st.session_state['name']
            username = st.session_state['username']
            st.markdown(f"Hello, {name}({username}) :smile:")
            st.markdown("Here, you'll explore endless possibilities for creativity and art. We offer a diverse range of AIGC image applications, whether you want to use AI to generate artistic ideas or do image post-processing, our App Store has the right apps for you. Feel free to try out various AI art tools.")
            st.markdown("Thank you for choosing ComfyFlowApp, and we look forward to seeing the fantastic creations you'll make. Happy creating!")
            
        