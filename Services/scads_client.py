import os
from openai import OpenAI


client = OpenAI(
    api_key="sk-_bvtwZ59ZZ-UJIn5swGKDA",
    base_url="https://llm.scads.ai/v1"
)

def ask_llm(prompt: str, model: str = "alias-ha"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content