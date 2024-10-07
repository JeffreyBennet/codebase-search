from app.services.llm.openai.openai_client import OpenAIClient

class LLM:
    def __init__(self, api_key: str, provider: str = "openai", model: str = "gpt-3.5-turbo", api_base_url: str = None):
        self.provider = provider
        self.model = self._initialize_model(provider, model, api_key, api_base_url)

    def _initialize_model(self, provider: str, model: str, api_key: str, api_base_url: str = None):
        if provider.lower() == 'openai':
            return OpenAIClient(model, api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def execute_query(self, prompt: str) -> str:
        return self.model.execute_query(prompt)