import streamlit as st
import asyncio
from travel_agent import get_travel_plan
import os

# Set page config
st.set_page_config(
    page_title="✈️ Travel Planning Assistant",
    page_icon="✈️",
    layout="wide"
)

# Check URL parameters for admin mode
is_admin = st.query_params.get("admin", "false").lower() == "true"
model = st.query_params.get("model", "gpt-4o-mini")

if model:
    os.environ["MODEL"] = model
# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for OpenAI key input
with st.sidebar:
    st.title("Settings")
    if is_admin:
        # In admin mode, get key from secrets.toml
        openai_key = st.secrets.get("OPENAI_API_KEY", "")
        if not openai_key:
            st.error("OpenAI API key not found in secrets.toml")
    else:
        # In normal mode, get key from user input
        openai_key = st.text_input("Enter your OpenAI API Key:", type="password")
    
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        st.success("API Key configured!")
    else:
        st.warning("Please enter your OpenAI API Key to use the assistant")

# Title and description
st.title("✈️ Travel Planning Assistant")
st.markdown("""
    Plan your perfect trip with our AI travel assistants! 
    Enter your travel request below and get a detailed itinerary with local insights and language tips.
""")

# User input
user_input = st.text_area(
    "Enter your travel request (e.g., 'Plan a 3 day trip to rameswaram, danushkodi, kanyakumari.'):",
    height=100,
    key="user_input"
)

# Initialize processing state in session state
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Submit button
submit_button = st.button(
    "Get Travel Plan",
    disabled=st.session_state.is_processing
)

async def process_travel_plan(user_input, response_placeholder):
    """Process the travel plan and update the UI"""
    full_response = ""
    async for response in get_travel_plan(user_input):
        # The response is a TaskResult object, we need to get the message content
        if hasattr(response, 'content'):
            full_response += response.content + "\n\n"
        response_placeholder.markdown(full_response)
    return full_response

if submit_button and user_input:
    # Set processing state
    st.session_state.is_processing = True
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Create a chat message container for the assistant
    with st.chat_message("assistant"):
        # Create a placeholder for the streaming response
        response_placeholder = st.empty()
        
        # Get travel plan responses with spinner
        with st.spinner("Generating your travel plan..."):
            try:
                # Stream responses as they come in
                full_response = asyncio.run(process_travel_plan(user_input, response_placeholder))
                
                # Add final response to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Reset processing state
                st.session_state.is_processing = False
elif submit_button:
    st.warning("Please enter a travel request.")
    st.session_state.is_processing = False

# Display chat history
st.markdown("### Chat History")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) 
