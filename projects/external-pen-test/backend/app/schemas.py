from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class UserBase(BaseModel):
    username: str
    role: Optional[str] = "analyst"


class UserCreate(UserBase):
    password: str = Field(min_length=12)


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class TargetBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: HttpUrl
    environment: Optional[str] = "production"


class TargetCreate(TargetBase):
    pass


class Target(TargetBase):
    id: int

    class Config:
        orm_mode = True


class FindingBase(BaseModel):
    title: str
    description: str
    severity: str


class FindingCreate(FindingBase):
    target_id: int


class Finding(FindingBase):
    id: int
    target_id: int
    reporter_id: Optional[int]
    created_at: datetime

    class Config:
        orm_mode = True


class ExploitationBase(BaseModel):
    vector: str
    result: str


class ExploitationCreate(ExploitationBase):
    target_id: int


class Exploitation(ExploitationBase):
    id: int
    target_id: int
    operator_id: Optional[int]
    executed_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ScanRequest(BaseModel):
    target_id: int


class ScanResult(BaseModel):
    findings: List[Finding]


class HealthResponse(BaseModel):
    status: str
    database: str
