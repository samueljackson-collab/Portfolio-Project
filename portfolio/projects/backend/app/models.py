from pydantic import BaseModel, HttpUrl


class Project(BaseModel):
    id: str
    name: str
    description: str
    tags: list[str]
    url: HttpUrl
