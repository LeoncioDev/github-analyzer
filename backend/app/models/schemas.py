# app/models/schemas.py
from pydantic import BaseModel

class GithubInput(BaseModel):
    github_url: str
