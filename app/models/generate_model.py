from pydantic import BaseModel, Field

class GenerateCodeRequest(BaseModel):
    user_prompt: str
    project_name: str
    provider: str = "openai"
    model: str = "gpt-3.5-turbo"