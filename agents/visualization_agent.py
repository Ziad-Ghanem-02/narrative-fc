from Services.scads_client import ask_llm


class VisualizationAgent:

    def __call__(self, state):

        code = self.generate_code(
            state["question"],
            state["evidence"]
        )

        namespace = {}

        try:
            exec(code, namespace)

            charts = namespace.get("generated_charts", [])

        except Exception as e:

            print("\nVisualization Error:\n")
            print(e)

            charts = []

        return {

            "charts": charts

        }

    def generate_code(self, question, evidence):

        prompt = f"""
You are an expert Python data visualization engineer.

Research Question:
{question}

Evidence Report:
{evidence}

Your task:

Read the entire evidence report.

For EVERY important statistical fact that can be visualized,
generate ONE chart.

Requirements:

- Use matplotlib only.
- Save every figure inside a folder named charts/.
- Create the folder if it does not exist.
- Produce one chart per important finding.
- Ignore facts that cannot reasonably be visualized.
- Use meaningful filenames.
- Use descriptive titles.
- Label every axis.
- Add legends whenever multiple series exist.
- Use line charts for historical trends.
- Use grouped bar charts for comparisons.
- Use horizontal bar charts for rankings.
- Use pie charts only for distributions.

At the beginning include:

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Also create:

os.makedirs("charts", exist_ok=True)

At the end create a variable named:

generated_charts

Example:

generated_charts = [
    "charts/goals.png",
    "charts/upsets.png"
]

Return ONLY executable Python code.

Do NOT use markdown.

Do NOT explain anything.

Do NOT include ```python.
"""

        print("Calling LLM...")
        return ask_llm(prompt)
        print("LLM returned.")