# FILE NAME: agent/sql_agent.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder # <-- 1. IMPORT ADDED
from langchain_core.output_parsers import JsonOutputParser
from agent.database_manager import DatabaseManager
from agent.llm_manager import LLMManager

class SQLAgent:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.llm_manager = LLMManager()

    def generate_validated_sql(self, state: dict) -> dict:
        schema = self.db_manager.get_schema(state['uuid'])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data analyst specializing in oceanographic data. Your goal is to answer a user's question by generating a single, valid SQLite query.

Analyze the user's question, the chat history, and the provided database schema.

Rules for the SQL query:
- Use only the tables and columns provided in the schema (`buoys`, `buoy_metadata`, `parameter_data`).
- `parameter_value` is stored as text and must be CAST to a number (e.g., `CAST(parameter_value AS REAL)`) for calculations like AVG, SUM, MIN, MAX.
- For questions about time or "latest/last", use the `observation_date` column and `ORDER BY observation_date DESC`.
- When filtering by a parameter (e.g., 'air temperature'), use the `parameter_name` column.
- Return ONLY a single JSON object with one key: "sql_query".
- If the question cannot be answered from the schema, set "sql_query": "NOT_RELEVANT".

---
EXAMPLE:
Question: What was the average air pressure for buoy AD08?
Response:
{{
 "sql_query": "SELECT AVG(CAST(parameter_value AS REAL)) AS average_air_pressure FROM parameter_data WHERE buoy_id = 'AD08' AND parameter_name = 'Air Pressure'"
}}
---
"""),
            MessagesPlaceholder(variable_name="chat_history"), # <-- 2. CHAT HISTORY ADDED TO PROMPT
            ("human", "Schema: {schema}\nQuestion: {query}\nResponse:")
        ])
        
        response = self.llm_manager.invoke(
            prompt, 
            schema=schema, 
            query=state["query"],
            chat_history=state["chat_history"] # <-- 3. CHAT HISTORY PASSED TO AI
        )
        
        cleaned_response_content = response.content.strip().replace("```json", "").replace("```", "")
        result = JsonOutputParser().parse(cleaned_response_content)

        if result["sql_query"] == "NOT_RELEVANT":
            return {"sql_query": "NOT_RELEVANT", "sql_valid": False}
        
        return {"sql_query": result["sql_query"], "sql_valid": True}

    def execute_sql(self, state: dict) -> dict:
        if not state['sql_valid']:
            return {"results": {"error": "Invalid SQL query."}}
        results = self.db_manager.execute_query(state['uuid'], state["sql_query"])
        return {"results": {"results": results}}