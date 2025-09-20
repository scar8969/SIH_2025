# FILE NAME: my_agent/DataFormatter.py

class DataFormatter:
    def format_data_for_visualization(self, state: dict) -> dict:
        visualization = state.get('visualization', 'none')
        results = state.get('results', {})
        data = results.get('results', [])
        
        if not data or isinstance(data, dict) and data.get("error") or visualization == "none":
            return {"formatted_data_for_visualization": None}

        formatted_data = {
            "type": visualization,
            "data": data
        }
        return {"formatted_data_for_visualization": formatted_data}