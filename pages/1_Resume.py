import streamlit as st
import utils.backend_utils as backend, utils.frontend_utils as frontend, utils.chatbot_utils as chatbot

st.set_page_config(layout='wide', page_title='Resume', page_icon=":paper:")

frontend.load_css()
chatbot.create_sidebar()

st.markdown("<h1 class='animated-widget' style='text-align: center; color: white;'>Osher's Resume</h1>", unsafe_allow_html=True)


backend.download_multiple_google_doc_files()

resume_markdown = backend.read_and_correct_resume_markdown()
st.markdown(resume_markdown, unsafe_allow_html=True)

st.divider()


frontend.resume_view_and_download()