from pydantic import BaseModel, Field

class RetrieveCodeRequest(BaseModel):
    hash: str