from dotenv import load_dotenv

load_dotenv()  ## loading all the environment variables

import os

import google.generativeai as genai
import streamlit as st

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## function to load Gemini Pro model and get repsonses
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])


def get_gemini_response(question):

    response = chat.send_message(question, stream=True)
    return response


##initialize our streamlit app

st.set_page_config(page_title="Gemini LLM QA Chatbot")

st.header("Gemini LLM Application")

# Sidebar for instructions
st.sidebar.title("Gemini QA Chat")
st.sidebar.image(
    "https://img.freepik.com/free-vector/graident-ai-robot-vectorart_78370-4114.jpg?semt=ais_hybrid",
    caption="Your AI Assistant",
    use_container_width=True,
)

st.sidebar.title("Instructions 📜")
st.sidebar.markdown(
    """
    1. Enter your question in the input box.
    2. Click the **Ask the question** button.
    3. View the bot's response and the chat history.
    4. To clear the session, refresh the page.
    
    **Note:** Chat history is stored during the session.
    """
)

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# input section
with st.container():
    st.subheader("Interact with the Bot:")
    input = st.text_input("Type your question here: ", key="input")
    submit = st.button("Ask the question")

# Chat Functionality
if submit and input:
    response = get_gemini_response(input)
    # Add user query and response to session state chat history
    st.session_state["chat_history"].append(("You", input))
    st.subheader("The Response is: ")
    for chunk in response:
        st.write(chunk.text)
        st.session_state["chat_history"].append(("LLM Bot", chunk.text))

# Display chat history
st.subheader("The Chat History 📝: ")
chat_container = st.container()

if st.session_state["chat_history"]:
    with chat_container:
        for role, text in st.session_state["chat_history"]:
            if role == "You":
                st.markdown(f"**🧑 {role}:** {text}")
            else:
                st.markdown(f"**🤖 {role}:** {text}")
else:
    st.info("No chat history yet. Start a conversation!")
