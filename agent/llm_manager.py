# FILE NAME: my_agent/llm_manager.py

import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMManager:
    def __init__(self):
        # Configure the ChatOpenAI client to use OpenRouter's API
        self.llm = ChatOpenAI(
            # 1. Set the model name to the one you want from OpenRouter
            model="x-ai/grok-4-fast:free",
            
            # 2. Use your OpenRouter API key
            api_key=os.getenv("OPENROUTER_API_KEY"),
            
            # 3. Point the client to the OpenRouter API endpoint
            base_url="https://openrouter.ai/api/v1",
            
            # 4. Add required headers for OpenRouter's free models
            default_headers={
                "HTTP-Referer": "http://localhost:3000", # Can be your project URL or a placeholder
                "X-Title": "Buoy Data Chatbot",       # Can be your project name
            }
        )

    def invoke(self, prompt: ChatPromptTemplate, **kwargs) -> str:
        chain = prompt | self.llm
        print(f"---LOG: Using model: {self.llm.model_name} via OpenRouter---")
        response = chain.invoke(kwargs)
        return response