# Q&A Chatbot for Invoice
# from langchain.llms import OpenAI

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import pathlib
import textwrap

import google.generativeai as genai
import streamlit as st
from PIL import Image

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## Function to load OpenAI model and get respones


def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([input, image[0], prompt])
    return response.text


def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        # Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,  # Get the mime type of the uploaded file
                "data": bytes_data,
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")


##initialize our streamlit app
st.set_page_config(page_title="Gemini Invoice Chatbot")

# sidebar
st.sidebar.title("Gemini Application")
st.sidebar.write(
    "Use this application to upload an invoice image and ask questions about it."
)
st.sidebar.image(
    "https://img.freepik.com/free-vector/graident-ai-robot-vectorart_78370-4114.jpg?semt=ais_hybrid",
    caption="Your AI Assistant",
    use_container_width=True,
)
st.sidebar.markdown(
    """
    ### Quick Tips:
    - Ensure the invoice image is clear and legible.
    - Ask specific questions, e.g., "What is the total amount?"
    - Supported formats: JPG, JPEG, PNG
    """
)

# header
st.header("Gemini Application")
st.markdown(
    """
    **Welcome to the Gemini Application!**
    This tool allows you to upload an invoice image and ask questions to understand its content better.
    Simply upload an image and type your question below to get started.
    """
)

# input section
input = st.text_input(
    "Input Prompt: ", placeholder="e.g., What is this invoice about?", key="input"
)
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# display uploaded image
image = ""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_container_width=True)


submit = st.button("Tell me about the image")

input_prompt = """
               You are an expert in understanding invoices.
               You will receive input images as invoices &
               you will have to answer questions based on the input image
               """

## If ask button is clicked

if submit:
    if uploaded_file is None:
        st.error("Please upload an invoice image before submitting.")
    elif not input.strip():
        st.error("Please enter a question before submitting.")
    else:
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(input_prompt, image_data, input)
        st.subheader("The Response is")
        st.write(response)


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
