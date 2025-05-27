import streamlit as st
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import chromadb
import logging
import re
import os
import chatbot.chatbot_train as chatbot_train

MODEL_PATH = "C:\\Users\\Osher N Boudara\\.cache\\gpt4all\\Phi-3-mini-4k-instruct.Q4_0.gguf"
VECTOR_DB_DIR = "db"

# Load model
@st.cache_resource
def load_llm():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=4096,
        n_threads=6,
        n_gpu_layers=35,
        temperature=0.7,
        stop=["User:", "Assistant:"]
    )
@st.cache_resource
def load_embedder():
    return SentenceTransformer("all-MiniLM-L6-v2")

@st.cache_resource
def load_vectorstore():
    client = chromadb.PersistentClient(path=VECTOR_DB_DIR)
    return client.get_or_create_collection("osher_docs")

llm = load_llm()
embedder = load_embedder()
vectorstore = load_vectorstore()

def extract_keywords_from_resume(resume_dir):
    keywords = set()
    for filename in os.listdir(resume_dir):
        if filename.endswith(".md") or filename.endswith(".txt"):
            with open(os.path.join(resume_dir, filename), "r", encoding="utf-8") as f:
                text = f.read()
                headers = re.findall(r"#+\s*([^\n]+)", text)
                bolded = re.findall(r"\*\*([^\*]+)\*\*", text)
                italicized = re.findall(r"\*([^\*]+)\*", text)
                for group in [headers, bolded, italicized]:
                    for item in group:
                        for word in re.findall(r"\b[a-zA-Z][a-zA-Z\-']+\b", item):
                            if len(word) > 2:
                                keywords.add(word.lower())
                for word in re.findall(r"\b[A-Z][a-zA-Z\-']+\b", text):
                    if len(word) > 2:
                        keywords.add(word.lower())
    return list(keywords)

RESUME_DIR = os.path.join(os.getcwd(), "resume")
AUTO_KEYWORDS = extract_keywords_from_resume(RESUME_DIR)

def retrieve_and_answer(query):
    # General responses as before...
    general_responses = {
        "hi how are you": "I'm doing well, thank you for asking! How can I help you today?",
        "hello how are you": "I'm doing well, thank you for asking! How can I help you today?",
        "hi how are you?": "I'm doing well, thank you for asking! How can I help you today?",
        "hello how are you?": "I'm doing well, thank you for asking! How can I help you today?",
        "how are you": "I'm doing well, thank you for asking! How can I help you today?",
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
        results = vectorstore.query(query_embeddings=[query_embedding], n_results=5)
    except Exception as e:
        return f"An error occurred while querying the database: {str(e)}"

    docs = results.get("documents", [])
    docs = [doc for sublist in docs for doc in (sublist if isinstance(sublist, list) else [sublist])]
    context = "\n".join(docs)

    # Only check if context is not empty
    if not context.strip():
        return "I'm sorry, I can only answer questions about Osher Boudara or general small talk."

    prompt = f"""You are Rebbe, an assistant who answers ONLY the user's question below, using ONLY the provided context.
Provide a single, concise answer to the user's question. Do NOT answer any other questions. Do NOT generate any additional questions or answers.
If the answer is not in the context, say: "I'm sorry, I can only answer questions about Osher Boudara or general small talk."
Do NOT make up any information or use knowledge outside the context. Do not infer or guess.

Context:
{context}

User's Question: {query}
"""

    try:
        response = llm(prompt, max_tokens=150)
        answer = response["choices"][0]["text"].strip()
        # Remove lines starting with dashes or section headers
        cleaned_lines = []
        for line in answer.split('\n'):
            if line.strip() and not line.strip().startswith("-") and not re.match(r"^[#\u25A0\u25CF]", line.strip()):
                cleaned_lines.append(line.strip())
        answer = " ".join(cleaned_lines)
        # Keep only the first sentence if needed
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
        st.markdown("### 💬 Chat with Rebbe! (BETA)")
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
        # Display chat history (newest at bottom)
        for sender, msg in st.session_state.chat_history:
            with st.chat_message("user" if sender == "User" else "assistant"):
                if sender == "Rebbe":
                    st.markdown(f"**Rebbe:** {msg}")
                else:
                    st.markdown(msg)