from pydantic import BaseModel
from typing import Optional, List


class User(BaseModel):
    username: str
    password: str
    email: str


class Token(BaseModel):
    user_id: int
    token: str
    created_at: str
    

class Articles(BaseModel):
    user_id: int
    title: str
    author: str
    content: str
    image: str
    
    

def check_token_expiry():
    return