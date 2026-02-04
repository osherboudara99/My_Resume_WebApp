import streamlit as st
import os
import streamlit.components.v1 as components
from streamlit_pdf_viewer import pdf_viewer 
import utils.backend_utils as backend
import time




dir_path = os.getcwd()

def load_css(file_name=os.path.join(dir_path, 'utils', 'style.css')):
    with open(file_name) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

def resume_view_and_download(resume_pdf_path = backend.resume_pdf_path, resume_download_name=backend.resume_name):
    with st.expander('View Resume PDF'):
        pdf_viewer(resume_pdf_path)



    st.download_button("Download Resume", data=backend.pdf_reader(resume_pdf_path), file_name=resume_download_name)


def certification_view(cert_name, cert_name_display, credential_link=None, dir_path=dir_path, validate=None):
    cert_path = os.path.join(dir_path, 'certifications', cert_name)


    with st.container():
        with st.expander(f'View {cert_name_display} PDF'):
            width = "100%"
            if cert_name == 'Osher_B_ml_specialization_UW_Coursera_cert.pdf':
                width = 700
            
        
            pdf_viewer(cert_path, width=width, height=1000)
            if credential_link:
                st.markdown(f'Link to [{cert_name_display}]({credential_link}) credential/badge')
        
            st.download_button(f"Download {cert_name_display}", data=backend.pdf_reader(cert_path), file_name=cert_name, mime='application/pdf')

def create_repo_sort(repos):

    st.markdown("""
        <style>
        /* General widget text color (labels, selectbox) */
        .stSelectbox > div, .stRadio > div,
        label, .stSelectbox label, .stRadio label {
            color: white !important;
        }

        /* Force dropdown options to be white */
        div[role="listbox"] > div {
            color: white !important;
            background-color: #1e1e1e !important;
        }

        /* Force radio button text to white */
        div[data-baseweb="radio"] label span {
            color: white !important;
        }

        /* Optional: override selected radio option styling */
        div[data-baseweb="radio"] input:checked + div > label > span {
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)

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
            options=["Descending", "Ascending"],
            horizontal=True,
            key="sort_order"
        )

    reverse = sort_order == "Descending"

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
            # if repo['fork']:
            #     st.markdown("**Forked:** Yes")
            if repo['stargazers_count'] > 0 or repo['forks_count'] > 0:
                st.markdown(f"⭐ Stars: {repo['stargazers_count']} | 🍴 Forks: {repo['forks_count']}")
            st.markdown("---")


def home_page_header_setup():
    st.markdown("<h1 class='animated-widget' justify-content: center; style='text-align: center; color: white;'>Osher Boudara</h1>", unsafe_allow_html=True)


    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; gap: 12px;">

    <div style="background-color: #1e1e3f; padding: 10px; border-radius: 10px;">
        <a href="https://www.linkedin.com/in/osher-boudara-a612921b5/" target="_blank">
        <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="#ffffff">
            <path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1 4.98 2.12 4.98 3.5zM0 24h5V7H0v17zm7.5-17h4.7v2.5h.07c.66-1.25 2.3-2.5 4.73-2.5 5.05 0 5.98 3.32 5.98 7.63V24h-5v-7.33c0-1.75-.03-4-2.43-4s-2.8 1.9-2.8 3.87V24h-5V7z"/>
        </svg>
        </a>
    </div>

    <div style="background-color: #1e1e3f; padding: 10px; border-radius: 10px;">
        <a href="https://www.github.com/osherboudara99/" target="_blank">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="#ffffff" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 0C5.37 0 0 5.37 0 12C0 17.3 3.44 21.8 8.2 23.3C8.8 23.4 9 23.1 9 22.8V20.7C5.9 21.4 5.2 19.4 5.2 19.4C4.6 18 3.8 17.6 3.8 17.6C2.7 16.9 3.9 17 3.9 17C5.1 17.1 5.7 18.3 5.7 18.3C6.8 20.1 8.5 19.6 9.2 19.3C9.3 18.5 9.6 17.9 9.9 17.6C7.2 17.3 4.4 16.3 4.4 11.6C4.4 10.3 4.9 9.2 5.7 8.3C5.5 8 5.1 6.7 5.9 5C5.9 5 6.9 4.6 9 6.1C10 5.8 11 5.7 12 5.7C13 5.7 14 5.8 15 6.1C17.1 4.6 18.1 5 18.1 5C18.9 6.7 18.5 8 18.3 8.3C19.1 9.2 19.6 10.3 19.6 11.6C19.6 16.3 16.8 17.3 14.1 17.6C14.6 18 15 18.7 15 19.7V22.8C15 23.1 15.2 23.4 15.8 23.3C20.6 21.8 24 17.3 24 12C24 5.37 18.63 0 12 0Z"/>
        </svg>
        </a>
    </div>

    </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

    components.html("""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/typed.js@2.0.12"></script>
        </head>
        <h2 style='text-align: center; color: white;'>
            <div style="font-size:24px; font-weight:bold;">
                <span>I am </span><span id="typed-text" ></span>
            </div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    var typed = new Typed('#typed-text', {
                        strings: ["a Python Developer.", "a Data Scientist.", "a Solutions Architect.", "a Musician.", "a Cloud Enthusiast.", 
                    "a Data Engineer.", "a Software Engineer.", "a Machine Learning Engineer."],
                        typeSpeed: 100,
                        backSpeed: 50,
                        loop: true,
                        showCursor: false,
                        backDelay: 1000
                    });
                });
            </script>
            </script>

        </h2>
        </html>
        """, height=60)



    img_base64 = backend.get_base64_image(os.path.join(dir_path, 'resume', 'self.jpeg'))

    st.markdown(f"""
    <div style="display: flex; flex-direction: row; align-items: center; background-color: #1e1e3f; padding: 30px; border-radius: 15px; color: white; gap: 30px;">
        <div style="display: flex; justify-content: center; align-items: center;">
            <img src="{img_base64}" style="width: 200px; border-radius: 12px;" />
        </div>
        <div style="max-width: 850px; font-size: 16px; line-height: 1.6;">
            <p>
            As a Senior Data Scientist at Cognizant, I lead and develop projects in data science initiatives for the Crop Science division of a global Fortune 500 client. I use my data science skillset to support stakeholders and deliver solutions.
            </p>
            <p>
            I have a B.S. in Computer Science and a minor in Statistics from California State University, Northridge, where I graduated with honors. I am passionate about conducting statistical research and transforming dataframes into actionable insights. My expertise in machine learning, generative AI and cloud-based architectures have allowed me to develop scalable tools that provide unique solutions.
            </p>
            <p>
            Fun facts about me: I'm bilingual and currently based in Los Angeles, CA. I enjoy making music, trying new foods, and exploring the world around me. I'm also a fan of the Los Angeles Rams.
            </p>
            <p>
            Chat with my friend, Rebbe, to learn more about me and my work!
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.write()
    st.markdown('---')

    st.write()

    st.title(f"My GitHub Repositories")
    st.markdown("<hr style='border:1px solid #ccc' />", unsafe_allow_html=True)