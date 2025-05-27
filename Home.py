import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout='wide', page_title='Home', page_icon=":house:")

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

repos = frontend.create_repo_sort(repos)

st.markdown('---')

frontend.display_repos(repos)





