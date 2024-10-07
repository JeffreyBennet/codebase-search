import openai

class EmbeddingService:
    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key
    
    def embed_code_chunk(self, code_chunk):
        """Generate an embedding for a given code chunk using OpenAI."""
        response = openai.Embedding.create(
            input=code_chunk,
            engine="text-embedding-ada-002"
        )
        return response['data'][0]['embedding']
