from pydantic import BaseModel

class NewSessionResponse(BaseModel):
    session_id: str
    message: str