import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
    )

# Define the system prompt for mental health focus
SYSTEM_PROMPT = """You are a compassionate and knowledgeable mental health assistant. Your role is to:
1. Provide empathetic and supportive responses to mental health questions
2. Offer general mental health information and coping strategies
3. Encourage seeking professional help when appropriate
4. Maintain a non-judgmental and safe space for discussions
5. Never provide medical diagnoses or replace professional medical advice
6. Use evidence-based information while keeping responses accessible
7. Prioritize user safety and well-being in all interactions

Important: Always include a disclaimer when appropriate that you are an AI assistant and not a replacement for professional mental health care."""

# Initialize session state for message history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": "Hello! I'm here to discuss mental health topics and provide support. "
         "While I can offer information and general guidance, please remember that I'm an AI assistant "
         "and not a substitute for professional mental health care. How can I help you today?"}
    ]

# Set page configuration
st.set_page_config(
    page_title="Mental Health Assistant",
    page_icon="🧠",
    layout="wide"
)

# Main title in the app
st.title("Mental Health Assistant")

# Display chat messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
if prompt := st.chat_input("What's on your mind?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Get response from OpenAI
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                temperature=0.7,
                max_tokens=800,
                stream=True
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.write(full_response + "▌")
            
            message_placeholder.write(full_response)
            
            # Add assistant's response to message history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            st.error(error_message) 