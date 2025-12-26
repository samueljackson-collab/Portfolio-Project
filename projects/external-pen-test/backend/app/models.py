from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(128), nullable=False)
    role = Column(String(50), default="analyst")

    findings = relationship("Finding", back_populates="reporter")
    exploitations = relationship("Exploitation", back_populates="operator")


class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(255), nullable=False)
    environment = Column(String(50), default="production")

    findings = relationship("Finding", back_populates="target", cascade="all, delete-orphan")
    exploitations = relationship("Exploitation", back_populates="target", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    target = relationship("Target", back_populates="findings")
    reporter = relationship("User", back_populates="findings")


class Exploitation(Base):
    __tablename__ = "exploitations"

    id = Column(Integer, primary_key=True, index=True)
    vector = Column(String(200), nullable=False)
    result = Column(Text, nullable=False)
    target_id = Column(Integer, ForeignKey("targets.id"), nullable=False)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow)

    target = relationship("Target", back_populates="exploitations")
    operator = relationship("User", back_populates="exploitations")
