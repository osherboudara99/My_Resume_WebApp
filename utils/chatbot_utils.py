import streamlit as st
import openai
from sentence_transformers import SentenceTransformer
import sys
# Add pysqlite3 support for Streamlit Cloud
import platform
if platform.system() != "Windows":
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


import chromadb
import re

@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_vectorstore():
    client = chromadb.PersistentClient(path="db")
    return client.get_or_create_collection("osher_docs")


def call_openai(prompt, max_tokens=150):
    try:
        client = openai.OpenAI(api_key=st.secrets.get("OPENAI_KEY") or os.getenv("OPENAI_KEY"))
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Rebbe, an assistant who answers ONLY the user's question below, using ONLY the provided context. Provide a single, concise answer. Do NOT answer any other questions. Do NOT generate any additional questions or answers. If the answer is not in the context, say: \"I'm sorry, I can only answer questions about Osher Boudara or general small talk.\" Do NOT make up any information or use knowledge outside the context. Do not infer or guess."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Check for quota error
        if hasattr(e, "status_code") and e.status_code == 429:
            try:
                error_data = e.response.json()
                if (
                    "error" in error_data
                    and error_data["error"].get("code") == "insufficient_quota"
                ):
                    return "⚠️ The OpenAI usage limits have been reached for this month. Please try again next month or contact the site owner."
            except Exception:
                pass
        print("OpenAI API error:", e)
        return "I'm sorry, I couldn't generate a response. Please try again later."

def retrieve_and_answer(query):
    general_responses = {
        "hi how are you": "I'm doing well, thank you for asking! How can I help you today?",
        "hello how are you": "I'm doing well, thank you for asking! How can I help you today?",
        "hi how are you?": "I'm doing well, thank you for asking! How can I help you today?",
        "hello how are you?": "I'm doing well, thank you for asking! How can I help you today?",
        "how are you": "I'm doing well, thank you for asking! How can I help you today?",
        "how are you?": "I'm doing well, thank you for asking! How can I help you today?",
        "what is your name": "I am Rebbe, an AI assistant here to answer questions about Osher Boudara based on the provided context.",
        "what is the weather like": "I’m unable to provide real-time weather information, but you can check your local weather service for the latest updates!",
        "who are you": "I am Rebbe, an AI assistant here to answer questions about Osher Boudara based on the provided context.",
        "hello": "Hello! How can I assist you today?",
        "hi": "Hi there! How can I assist you today?",
        "good morning": "Good morning! How can I assist you today?",
        "good evening": "Good evening! How can I assist you today?"
    }
    query_lower = query.lower().strip()
    if query_lower in general_responses:
        return general_responses[query_lower]

    # Embed the query
    try:
        query_embedding = embedder.encode([query.lower().strip()])[0].tolist()
    except Exception as e:
        return "An error occurred while processing your query."

    # Retrieve more relevant chunks
    try:
        results = vectorstore.query(query_embeddings=[query_embedding], n_results=15)
    except Exception as e:
        return f"An error occurred while querying the database: {str(e)}"

    docs = results.get("documents", [])
    docs = [doc for sublist in docs for doc in (sublist if isinstance(sublist, list) else [sublist])]
    context = "\n".join(docs)

    if not context.strip():
        return "I'm sorry, I can only answer questions about Osher Boudara or general small talk."

    prompt = f"""
        Context:
        {context}

        User's Question: {query}
    """

    try:
        answer = call_openai(prompt, max_tokens=150)
        # Remove lines starting with dashes or section headers
        cleaned_lines = []
        for line in answer.split('\n'):
            if line.strip() and not line.strip().startswith("-") and not re.match(r"^[#\u25A0\u25CF]", line.strip()):
                cleaned_lines.append(line.strip())
        answer = " ".join(cleaned_lines)
        answer = answer.split(".")[0].strip() + "."
        forbidden_entities = [
            "florida department of agriculture", "chief data officer", "mit", "berkeley", "brown university"
        ]
        if any(entity in answer.lower() for entity in forbidden_entities):
            return "I'm sorry, I can only answer questions about Osher Boudara or general small talk."
        return answer
    except Exception as e:
        return "I'm sorry, I couldn't generate a response. Please try again later."



def create_sidebar():
    

    with st.sidebar:
        st.markdown("### 💬 Chat with Rebbe!")
        st.markdown("Ask anything about Osher — resume, skills, projects, and more.")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        user_input = st.chat_input("Ask a question about Osher...")

        if user_input:
            with st.spinner("Rebbe is thinking..."):
                answer = retrieve_and_answer(user_input)
                # Remove unwanted prefixes and duplicate lines
                answer = answer.replace("<|assistant|>", "").replace("[ai]:", "").replace("== response ==", "").strip()
                lines = []
                for line in answer.split('\n'):
                    if line.strip() and line.strip() not in lines:
                        lines.append(line.strip())
                answer = "\n".join(lines)
            st.session_state.chat_history.append(("User", user_input))
            st.session_state.chat_history.append(("Rebbe", answer))
        
        # Display chat history 
        for sender, msg in st.session_state.chat_history:
            with st.chat_message("user" if sender == "User" else "assistant"):
                if sender == "Rebbe":
                    st.markdown(f"**Rebbe:** {msg}")
                else:
                    st.markdown(msg)

embedder = load_embedder()
vectorstore = load_vectorstore()

