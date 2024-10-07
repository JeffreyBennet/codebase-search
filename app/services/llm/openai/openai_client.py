from openai import OpenAI

class OpenAIClient:
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def execute_query(self, prompt: str) -> str:
        # Execute a query on the OpenAI model
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error executing query: {e}")
            return f"Error: {e}"
