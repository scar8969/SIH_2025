# In main.py

import json
from agent.workflow_manager import WorkflowManager # <-- Changed
# ... rest of the file is the same

def main():
    """Initializes and runs the SQL agent workflow."""
    workflow_manager = WorkflowManager()
    app = workflow_manager.create_workflow()

    print("Buoy Data SQL Agent is ready. Ask a question or type 'exit' to quit.")

    while True:
        query = input("\n> ")
        if query.lower() == 'exit':
            break

        # The 'uuid' is not used in this simplified version but is kept for compatibility
        inputs = {"query": query, "uuid": "12345"}
        
        final_state = app.invoke(inputs)

        # Print the final, structured output
        print(json.dumps(final_state, indent=2))

if __name__ == "__main__":
    main()