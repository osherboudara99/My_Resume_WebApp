import os

# Import and call the backend utility function
from utils import backend_utils as backend
backend.download_multiple_google_doc_files()

# Execute the chatbot training script using Python 3.13
os.system('py -3.13 -m chatbot.chatbot_train')