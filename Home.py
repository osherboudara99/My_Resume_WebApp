import sys
import types

# Prevent Streamlit from inspecting `torch.classes` which breaks things
sys.modules['torch.classes'] = types.SimpleNamespace()

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout='wide', page_title='Home', page_icon=":house:")

st.markdown("""
<style>
/* Hide rogue material icon text in sidebar */
span[aria-hidden="true"] {
    color: transparent !important;
    font-size: 0 !important;
}
</style>
""", unsafe_allow_html=True)

import utils.backend_utils as backend, utils.frontend_utils as frontend, utils.chatbot_utils as chatbot
import time
import os


dir_path = os.getcwd()

GITHUB_USERNAME = "osherboudara99"


# Call the function to load the CSS
frontend.load_css()

chatbot.create_sidebar()

frontend.home_page_header_setup()


repos = backend.get_repos(GITHUB_USERNAME)

if not repos:
    st.warning("🚧 Projects couldn't be retrieved at this time (e.g., GitHub API limit reached). Please try again later.")
else:
    repos = frontend.create_repo_sort(repos)
    frontend.display_repos(repos)








