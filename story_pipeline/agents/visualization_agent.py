class VisualizationAgent:
    def __call__(self, state):
        return {
            "charts": [
                {
                    "title": result["purpose"],
                    "columns": result["columns"],
                    "data": result["data"],
                }
                for result in state["results"]
            ]
        }