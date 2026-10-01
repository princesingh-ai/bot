from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's input query to the CRIEYA Assistant.")

class ChatResponse(BaseModel):
    response: str = Field(..., description="The generated AI textual response.")
