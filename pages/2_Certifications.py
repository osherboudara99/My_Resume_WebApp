import streamlit as st
import utils.backend_utils as backend
import utils.frontend_utils as frontend
import utils.chatbot_utils as chatbot

st.set_page_config(layout="wide", page_icon=':notebook:')

frontend.load_css()

chatbot.create_sidebar()

st.markdown("<h1 style='text-align: center; color: white;'>Certifications</h1>", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: white;'>Below are a few of my certifications. \
            For additional certifications, please check out my <a href=https://www.linkedin.com/in/osher-boudara-a612921b5/details/certifications/>LinkedIn</a></p>", unsafe_allow_html=True)
aws_ccp_cert_name = 'Osher_B_AWS_CCP_cert.pdf'
azure_fund_cert_name = 'Osher_B_AZ900_cert_rotated.pdf'
usdl_dbtech_cert_name = 'Osher_B_Database_Tech_USDL_cert.pdf'
uw_ml_cert_name = 'Osher_B_ml_specialization_UW_Coursera_cert.pdf'

aws_ccp_display_name = 'AWS Certified Cloud Practitioner'
azure_fund_display_name = 'Microsoft Certified: Azure Fundamentals (AZ900)'
usdl_dbtech_display_name = 'Database Technician Apprenticeship from US Department of Labor'
uw_ml_display_name = 'Machine Learning Specialization from University of Washington through Coursera'

aws_ccp_link = 'https://www.credly.com/badges/6245d5af-8a5c-4dc1-8591-382b6f342d6a/'
azure_fund_link = 'https://learn.microsoft.com/en-us/users/osherboudara-7874/credentials/3e3599c5dccdd406?ref=https%3A%2F%2Fwww.linkedin.com%2F'
uw_ml_link = 'https://www.coursera.org/account/accomplishments/specialization/ADDB2SJ6MNF3'


frontend.certification_view(uw_ml_cert_name, uw_ml_display_name, uw_ml_link)
frontend.certification_view(aws_ccp_cert_name, aws_ccp_display_name, aws_ccp_link)
frontend.certification_view(azure_fund_cert_name, azure_fund_display_name, azure_fund_link)
frontend.certification_view(usdl_dbtech_cert_name, usdl_dbtech_display_name)
