import streamlit as st
import os
import streamlit.components.v1 as components
from streamlit_pdf_viewer import pdf_viewer 
import utils.backend_utils as backend


dir_path = os.getcwd()

# Function to load CSS
def load_css(file_name=fr'{dir_path}\utils\style.css'):
    with open(file_name) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def create_aboutme(dir_path=dir_path):


    st.sidebar.markdown("<h1 style='text-align: center; color: white;'>Osher's Resume App</h1>", unsafe_allow_html=True)
    st.sidebar.image(fr'{dir_path}\resume\self.jpeg')
    st.sidebar.markdown("## __About Osher__")


    about = "I am a data scientist with a passion for transforming dataframes into actionable insights. \
    With a background in computer science and statistics, I specialize in building robust machine learning algorithms and conducting statistical analysis of any dataset that comes my way. \
    My expertise in Python, SQL and cloud-based architectures have allowed me to develop scalable tools that provide unique solutions."

    st.sidebar.write(about)

def resume_view_and_download(resume_pdf_path = backend.resume_pdf_path, resume_download_name=backend.resume_name):
    with st.expander('View Resume PDF'):
        pdf_viewer(resume_pdf_path)



    st.download_button("Download Resume", data=backend.pdf_reader(resume_pdf_path), file_name=resume_download_name)


def certification_view(cert_name, cert_name_display, credential_link=None, dir_path=dir_path, validate=None):
    cert_path = fr'{dir_path}\certifications\{cert_name}'


    with st.container():
        with st.expander(f'View {cert_name_display} PDF'):
            pdf_viewer(cert_path, width="100%", height=1000)
            if credential_link:
                st.markdown(f'Link to [{cert_name_display}]({credential_link}) credential/badge')
        
            st.download_button(f"Download {cert_name_display}", data=backend.pdf_reader(cert_path), file_name=cert_name, mime='application/pdf')

def create_repo_sort(repos):

    # Display sorting options in a single row using columns
    col1, col2 = st.columns([1, 1])

    with col1:
        sort_key = st.selectbox(
            "Sort by:",
            options=["updated_at", "created_at", "name"],
            format_func=lambda x: {"updated_at": "Last Updated", "created_at": "Created Date", "name": "Name"}[x],
            key="sort_key"
        )
    with col2:
        sort_order = st.radio(
            "Order:",
            options=["descending", "ascending"],
            horizontal=True,
            key="sort_order"
        )

    reverse = sort_order == "descending"

    if sort_key in ["updated_at", "created_at"]:
        sort_field = f"{sort_key}_dt"
        repos = sorted(repos, key=lambda r: r[sort_field], reverse=reverse)
    else:  # sort_key == "name"
        repos = sorted(repos, key=lambda r: r["name"].lower(), reverse=reverse)
    
    return repos


def display_repos(repos):
    for repo in repos:
        with st.container():
            st.markdown(f"### [{repo['name']}]({repo['html_url']})")
            st.markdown(f"**Description:** {repo['description'] or 'No description'}")
            st.markdown(f"**Created At:** {repo['created_time']} ({repo['created_relative']})")
            st.markdown(f"**Last Updated:** {repo['last_update']} ({repo['relative_time']})")
            st.markdown(f"**Language:** {repo['language'] or 'Not specified'}")
            st.markdown(f"**GitHub URL:** {repo['html_url']}")
            if repo['stargazers_count'] > 0 or repo['forks_count'] > 0:
                st.markdown(f"⭐ Stars: {repo['stargazers_count']} | 🍴 Forks: {repo['forks_count']}")
            st.markdown("---")