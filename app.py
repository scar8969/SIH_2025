# FILE NAME: app.py

import streamlit as st

from agent.workflow_manager import WorkflowManager 
import pandas as pd
from langchain_core.messages import HumanMessage, AIMessage

# --- Page Configuration ---
st.set_page_config(
    page_title="Buoy Data Chatbot",
    page_icon="🚤",
    layout="wide"
)

st.title("🚤 Buoy Data Chatbot (With Memory)")
st.write("Ask questions about the buoy data. The AI agent can remember your conversation.")

# --- Initialize the Agent ---
# This uses a Streamlit caching feature to load the agent only once.
@st.cache_resource
def get_workflow_app():
    """Initializes and returns the compiled LangGraph workflow."""
    workflow_manager = WorkflowManager()
    return workflow_manager.create_workflow()

app = get_workflow_app()

# --- Chat Interface ---
# Initialize chat history using LangChain message objects
if "langchain_messages" not in st.session_state:
    st.session_state.langchain_messages = []

# Display previous messages from history
for msg in st.session_state.langchain_messages:
    st.chat_message(msg.type).write(msg.content)

# Get new user input from the chat input box at the bottom
if prompt := st.chat_input("What was the average air pressure for AD08?"):
    # Display the new user message
    st.chat_message("human").write(prompt)

    # Prepare the inputs for the agent, including the chat history
    inputs = {
        "query": prompt,
        "uuid": "streamlit_user",
        "chat_history": st.session_state.langchain_messages
    }
    
    # Add the new user message to the history
    st.session_state.langchain_messages.append(HumanMessage(content=prompt))
    
    # Get the AI's response
    with st.spinner("The AI agent is thinking..."):
        final_state = app.invoke(inputs)

        answer = final_state.get("answer", "I couldn't find an answer.")
        
        # Display the AI's response
        with st.chat_message("ai"):
            st.markdown(answer)
            
            # Add the new AI message to the history
            st.session_state.langchain_messages.append(AIMessage(content=answer))

            # Display the data results in a table if they exist
            results_data = final_state.get("results", {}).get("results", [])
            if results_data and "error" not in results_data[0]:
                st.dataframe(pd.DataFrame(results_data))