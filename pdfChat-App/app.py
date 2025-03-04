import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from PyPDF2 import PdfReader

# Load environment variables
load_dotenv()
print(os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_response" not in st.session_state:
    st.session_state.current_response = ""
if "user_question" not in st.session_state:
    st.session_state.user_question = ""


# Function to extract text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# Split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)


# Store embeddings in FAISS
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


# Setup QA Chain
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. 
    If the answer is not available in the context, just say, "Answer is not available in the context". 
    Do not provide incorrect information.

    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    return load_qa_chain(model, chain_type="stuff", prompt=prompt)


# Handle user input and retrieve response
def user_input():
    user_question = (
        st.session_state.user_question
    )  # Fetch user question from session state
    if not user_question:
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    new_db = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()
    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True
    )

    ai_response = response["output_text"]

    # Store current response
    st.session_state.current_response = ai_response

    # Append to chat history
    st.session_state.chat_history.append(("You", user_question))
    st.session_state.chat_history.append(("🤖 AI", ai_response))

    # Clear input field after response
    st.session_state.user_question = ""


# Streamlit App Layout
st.set_page_config(page_title="RAG App")

# Sidebar Section
st.sidebar.title("Gemini RAG ChatApp 🤖")
st.sidebar.image(
    "https://miro.medium.com/v2/resize:fit:1400/1*SvokklbDo1pUdDijtMrc2Q.png",
    caption="Your AI Assistant",
    use_container_width=True,
)

st.sidebar.title("Instructions 📜")
st.sidebar.markdown(
    """
    1. Upload PDFs to create a knowledge base.
    2. Ask a question related to the content.
    3. View detailed AI-generated answers.
    4. All chat history is stored within the session.
    5. Refresh to clear the conversation.
    """
)

# Main Header
st.header("📄 Chat with Multiple PDFs using Gemini")
st.subheader("Upload PDFs and interact with AI")

# PDF Upload & Processing
with st.sidebar:
    pdf_docs = st.file_uploader("Upload PDF Files", accept_multiple_files=True)
    if st.button("Process PDFs"):
        with st.spinner("Extracting and Indexing..."):
            raw_text = get_pdf_text(pdf_docs)
            text_chunks = get_text_chunks(raw_text)
            get_vector_store(text_chunks)
            st.success("PDFs processed successfully!")

# User Question Input
st.subheader("Ask a Question 📩")
st.text_input("Type your question :", key="user_question", on_change=user_input)

# Display Current AI Response Below the Input
if st.session_state.current_response:
    st.subheader("🔹 AI Response:")
    st.write(st.session_state.current_response)

# Display Chat History at the Bottom
st.subheader("📝 Chat History")
if st.session_state.chat_history:
    chat_container = st.container()
    with chat_container:
        for role, text in st.session_state.chat_history:
            st.markdown(f"**{role}:** {text}")
else:
    st.info("No conversation history yet. Start chatting!")


st.markdown(
    """
<div style='text-align: center'>
    <small>
    &copy; 2025 AI Agents. All rights reserved by <a href="https://jahanzaibtayyab.com/">Jahanzaib Tayyab</a>.
    </small>
</div>
""",
    unsafe_allow_html=True,
)
