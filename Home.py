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

# Use `components.html` to properly execute JavaScript
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
                    strings: ["a Python Developer.", "a Data Scientist.", "a Solutions Architect.", 
                "a Data Engineer.", "a Software Engineer.", "a Machine Learning Engineer.", "a Streamlit Enthusiast."],
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



img_base64 = backend.get_base64_image(f"{dir_path}/resume/self.jpeg")

# HTML layout with flex row
st.markdown(f"""
<div style="display: flex; flex-direction: row; align-items: center; background-color: #1e1e3f; padding: 30px; border-radius: 15px; color: white; gap: 30px;">
    <div style="display: flex; justify-content: center; align-items: center;">
        <img src="{img_base64}" style="width: 200px; border-radius: 12px;" />
    </div>
    <div style="max-width: 850px; font-size: 16px; line-height: 1.6;">
        <p>
        As a Senior Data Scientist at Cognizant, I am leading and developing projects in data science and engineering teams for the crop science division of a global Fortune 500 company. I use my data science skillset to deliver solutions that meet the client's needs and expectations.
        </p>
        <p>
        I have a B.S. in Computer Science and a minor in Statistics from California State University, Northridge, where I graduated with honors. I am passionate about conducting statistical research and transforming dataframes into actionable insights. 
        </p>
        <p>
        Fun facts about me: I'm bilingual and currently based in Boston, MA. I enjoy making music, trying new foods, and exploring the world around me. I'm also a proud fan of the Los Angeles Rams.
        </p>
        <p>
        Chat with my friend Rebbe, to learn more about me and my work!
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

st.write()
st.markdown('---')

st.write()

st.title(f"My GitHub Repositories")
st.markdown("<hr style='border:1px solid #ccc' />", unsafe_allow_html=True)


repos = backend.get_repos(GITHUB_USERNAME)

repos = frontend.create_repo_sort(repos)

st.markdown('---')

frontend.display_repos(repos)





