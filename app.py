import os
import chainlit as cl
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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



@cl.on_chat_start
async def start_chat():
    """Initialize the chat session with system prompt."""
    # Initialize message history in the session
    cl.user_session.set("messages", [
        {"role": "system", "content": SYSTEM_PROMPT}
    ])
    
    await cl.Message(
        content="Hello! I'm here to discuss mental health topics and provide support. "
        "While I can offer information and general guidance, please remember that I'm an AI assistant "
        "and not a substitute for professional mental health care. How can I help you today?"
    ).send()

async def call_openai(query: str):
    """Handle the OpenAI API call and message management."""
    # Get current message history
    messages = cl.user_session.get("messages")
    # Add user message to history
    messages.append({"role": "user", "content": query})
    
    # Create message with empty content for streaming
    msg = cl.Message(content="", author="Assistant")
    
    try:
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=800,
            stream=True
        )
        
        # Stream the response
        for chunk in response:
            if chunk.choices[0].delta.content:
                await msg.stream_token(chunk.choices[0].delta.content)
                
        # Send the complete message
        await msg.send()
        
        # Add assistant's response to message history
        messages.append({"role": "assistant", "content": msg.content})
        cl.user_session.set("messages", messages)
        
    except Exception as e:
        error_message = f"I apologize, but I encountered an error: {str(e)}"
        await cl.Message(content=error_message).send()

@cl.on_message
async def chat(message: cl.Message):
    """Process incoming messages."""
    await call_openai(message.content) 