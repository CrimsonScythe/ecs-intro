from pydantic import BaseModel

class Book(BaseModel):
    
    name: str
    author: str

    class Config:
        orm_mode = True

