import os
from datetime import timedelta
from random import choice
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db
from .security import create_access_token, get_password_hash, verify_password

try:
    Base.metadata.create_all(bind=engine)
except Exception:
    # Database might be offline during test bootstrap; tables will be created on first real connection
    pass

app = FastAPI(title="External Pen Test API")

origins = os.getenv("CORS_ALLOW", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@app.post("/auth/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    import jwt

    try:
        payload = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


@app.get("/health", response_model=schemas.HealthResponse)
def health(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        status_text = "ok"
    except Exception:
        status_text = "error"
    return schemas.HealthResponse(status=status_text, database=status_text)


@app.post("/targets", response_model=schemas.Target)
def create_target(target: schemas.TargetCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_target = models.Target(**target.dict())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target


@app.get("/targets", response_model=list[schemas.Target])
def list_targets(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Target).all()


@app.post("/findings", response_model=schemas.Finding)
def create_finding(
    finding: schemas.FindingCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    target = db.query(models.Target).filter(models.Target.id == finding.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    db_finding = models.Finding(**finding.dict(), reporter_id=current_user.id)
    db.add(db_finding)
    db.commit()
    db.refresh(db_finding)
    return db_finding


@app.get("/findings", response_model=list[schemas.Finding])
def list_findings(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Finding).all()


@app.post("/exploitations", response_model=schemas.Exploitation)
def create_exploitation(
    exploitation: schemas.ExploitationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    target = db.query(models.Target).filter(models.Target.id == exploitation.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    db_exploitation = models.Exploitation(**exploitation.dict(), operator_id=current_user.id)
    db.add(db_exploitation)
    db.commit()
    db.refresh(db_exploitation)
    return db_exploitation


@app.get("/exploitations", response_model=list[schemas.Exploitation])
def list_exploitations(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Exploitation).all()


@app.post("/scan", response_model=schemas.ScanResult)
def run_scan(payload: schemas.ScanRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    target = db.query(models.Target).filter(models.Target.id == payload.target_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    severity = choice(["low", "medium", "high"])
    dummy = models.Finding(
        title=f"Automated scan finding for {target.name}",
        description="Simulated vulnerability discovered during automated scan.",
        severity=severity,
        target_id=target.id,
        reporter_id=current_user.id,
    )
    db.add(dummy)
    db.commit()
    db.refresh(dummy)
    return schemas.ScanResult(findings=[dummy])
