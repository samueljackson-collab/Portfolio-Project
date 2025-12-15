import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel, HttpUrl

from .scanner import scan_page

SECRET_KEY = os.environ.get("SECRET_KEY", "demo-secret-key-for-dev-only")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()
app = FastAPI(title="Web App Assessment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class Endpoint(BaseModel):
    id: int
    name: str
    path: str
    description: Optional[str] = None


class EndpointCreate(BaseModel):
    name: str
    path: str
    description: Optional[str] = None


class Page(BaseModel):
    id: int
    endpoint_id: int
    url: HttpUrl
    last_scanned: Optional[datetime] = None


class PageCreate(BaseModel):
    endpoint_id: int
    url: HttpUrl


class VulnerabilityFinding(BaseModel):
    id: int
    endpoint_id: int
    page_id: int
    title: str
    severity: str
    description: str
    rule: str
    created_at: datetime


class FindingCreate(BaseModel):
    endpoint_id: int
    page_id: int
    title: str
    severity: str
    description: str
    rule: str


class ScanRequest(BaseModel):
    endpoint_id: int
    url: HttpUrl


class ScanResponse(BaseModel):
    page: Page
    findings: List[VulnerabilityFinding]


# In-memory stores for demo purposes only
endpoints: List[Endpoint] = [
    Endpoint(id=1, name="Landing Page", path="/", description="Marketing site"),
    Endpoint(id=2, name="API", path="/api", description="Application API"),
]
pages: List[Page] = []
findings: List[VulnerabilityFinding] = []


# Auth helpers

def create_token(username: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub") or "anonymous"
    except JWTError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        ) from exc


@app.post("/login", response_model=Token)
def login(login_request: LoginRequest) -> Token:
    if not (secrets.compare_digest(login_request.username, "admin") and secrets.compare_digest(login_request.password, "password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token(login_request.username)
    return Token(access_token=token)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/endpoints", response_model=List[Endpoint])
def list_endpoints(user: str = Depends(get_current_user)) -> List[Endpoint]:  # pragma: no cover - dependency tested elsewhere
    return endpoints


@app.post("/endpoints", response_model=Endpoint, status_code=status.HTTP_201_CREATED)
def add_endpoint(endpoint: EndpointCreate, user: str = Depends(get_current_user)) -> Endpoint:
    new_id = max((e.id for e in endpoints), default=0) + 1
    created = Endpoint(id=new_id, **endpoint.model_dump())
    endpoints.append(created)
    return created


@app.get("/pages", response_model=List[Page])
def list_pages(user: str = Depends(get_current_user)) -> List[Page]:  # pragma: no cover
    return pages


@app.post("/pages", response_model=Page, status_code=status.HTTP_201_CREATED)
def add_page(page: PageCreate, user: str = Depends(get_current_user)) -> Page:
    if not any(e.id == page.endpoint_id for e in endpoints):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")
    new_id = max((p.id for p in pages), default=0) + 1
    created = Page(id=new_id, last_scanned=None, **page.model_dump())
    pages.append(created)
    return created


@app.get("/findings", response_model=List[VulnerabilityFinding])
def list_findings(user: str = Depends(get_current_user)) -> List[VulnerabilityFinding]:  # pragma: no cover
    return findings


@app.post("/findings", response_model=VulnerabilityFinding, status_code=status.HTTP_201_CREATED)
def add_finding(finding: FindingCreate, user: str = Depends(get_current_user)) -> VulnerabilityFinding:
    if not any(p.id == finding.page_id for p in pages):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    new_id = max((f.id for f in findings), default=0) + 1
    created = VulnerabilityFinding(id=new_id, created_at=datetime.now(timezone.utc), **finding.model_dump())
    findings.append(created)
    return created


@app.post("/scan-page", response_model=ScanResponse)
def scan_page_handler(payload: ScanRequest, user: str = Depends(get_current_user)) -> ScanResponse:
    if not any(e.id == payload.endpoint_id for e in endpoints):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Endpoint not found")

    page_id = max((p.id for p in pages), default=0) + 1
    page = Page(id=page_id, endpoint_id=payload.endpoint_id, url=payload.url, last_scanned=datetime.now(timezone.utc))
    pages.append(page)

    findings_payload = scan_page(payload.url)
    response_findings: List[VulnerabilityFinding] = []

    for finding in findings_payload:
        new_id = max((f.id for f in findings), default=0) + 1
        created = VulnerabilityFinding(
            id=new_id,
            endpoint_id=payload.endpoint_id,
            page_id=page_id,
            title=finding.title,
            severity=finding.severity,
            description=finding.description,
            rule=finding.rule,
            created_at=datetime.now(timezone.utc),
        )
        findings.append(created)
        response_findings.append(created)

    return ScanResponse(page=page, findings=response_findings)
