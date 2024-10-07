from pydantic import BaseModel

class SearchRequest(BaseModel):
    repo_url: str
    prompt: str
