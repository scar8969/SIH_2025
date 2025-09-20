# In my_agent/workflow_manager.py

from langgraph.graph import StateGraph, END
from agent.sql_agent import SQLAgent
from agent.data_formatter import DataFormatter
from typing import TypedDict, List, Any, Dict
from langchain_core.messages import BaseMessage # <-- Add this import

class AgentState(TypedDict):
    query: str
    uuid: str
    chat_history: List[BaseMessage] # <-- Add this line to store memory
    sql_query: str
    sql_valid: bool
    results: List[Any]
    answer: str
    visualization: str
    visualization_reason: str
    formatted_data_for_visualization: Dict[str, Any]
class WorkflowManager:
    def __init__(self):
        self.sql_agent = SQLAgent()
        self.data_formatter = DataFormatter()

    def create_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        workflow.add_node("generate_validated_sql", self.sql_agent.generate_validated_sql)
        workflow.add_node("execute_sql", self.sql_agent.execute_sql)
        workflow.add_node("generate_final_response", self.generate_final_response)
        workflow.add_node("format_data_for_visualization", self.data_formatter.format_data_for_visualization)
        
        workflow.set_entry_point("generate_validated_sql")
        workflow.add_edge("generate_validated_sql", "execute_sql")
        workflow.add_edge("execute_sql", "generate_final_response")
        workflow.add_edge("generate_final_response", "format_data_for_visualization")
        workflow.add_edge("format_data_for_visualization", END)
        return workflow.compile()
    
    def generate_final_response(self, state: dict) -> dict:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import JsonOutputParser

        if "error" in state["results"]:
            return {"answer": "There was an error executing the SQL query.", "visualization": "none"}

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant. Your job is to provide a final answer based on database results and recommend a visualization.

Respond in a single JSON object with three keys:
- "answer": A single, human-readable sentence summarizing the results.
- "visualization": The most suitable chart type: "bar", "pie", "line", or "none".
- "visualization_reason": A brief explanation for your chart choice.

Rules:
- For comparing categories vs. numbers (e.g., buoy vs. average value), use "bar".
- For time-series data (e.g., values over `observation_date`), use "line".
- For single values or text, use "none".
""",), 
            ("human", "Question: {query}\nResults: {results}\nResponse:")
        ])
        
        response = self.sql_agent.llm_manager.invoke(prompt, query=state["query"], results=state["results"])
        result = JsonOutputParser().parse(response.content)
        return result