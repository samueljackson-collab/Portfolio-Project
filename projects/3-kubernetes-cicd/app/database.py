"""
Database module with SQLAlchemy models and CRUD operations.

This module provides database connectivity demo for the Kubernetes CI/CD
application, including a Task model for demonstrating database operations.
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import enum

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=5,
    max_overflow=10,
    echo=os.getenv('SQL_ECHO', 'false').lower() == 'true'
)

# Create session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Base class for models
Base = declarative_base()


class TaskPriority(enum.Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(enum.Enum):
    """Task status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Task(Base):
    """Task model for database demo."""

    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default='medium')
    status = Column(String(20), default='pending')
    assignee = Column(String(100), nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                       onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'assignee': self.assignee,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Task(id={self.id}, title='{self.title}', status='{self.status}')>"


def init_db():
    """Initialize database and create tables."""
    Base.metadata.create_all(engine)
    print(f"Database initialized: {DATABASE_URL}")


def get_session():
    """Get a database session."""
    return Session()


def close_session():
    """Close the current session."""
    Session.remove()


# =============================================================================
# CRUD Operations
# =============================================================================

def get_all_tasks() -> List[Dict[str, Any]]:
    """Get all tasks from the database."""
    session = get_session()
    try:
        tasks = session.query(Task).order_by(Task.created_at.desc()).all()
        return [task.to_dict() for task in tasks]
    finally:
        close_session()


def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific task by ID."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        return task.to_dict() if task else None
    finally:
        close_session()


def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    assignee: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a new task."""
    session = get_session()
    try:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            assignee=assignee,
            due_date=due_date,
            status='pending',
            completed=False
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        close_session()


def update_task(task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing task."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return None

        # Update allowed fields
        allowed_fields = ['title', 'description', 'priority', 'status',
                         'assignee', 'due_date', 'completed']

        for field in allowed_fields:
            if field in data:
                setattr(task, field, data[field])

        task.updated_at = datetime.now(timezone.utc)
        session.commit()
        session.refresh(task)
        return task.to_dict()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        close_session()


def delete_task(task_id: int) -> bool:
    """Delete a task by ID."""
    session = get_session()
    try:
        task = session.query(Task).filter(Task.id == task_id).first()
        if not task:
            return False

        session.delete(task)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        raise e
    finally:
        close_session()


def get_tasks_by_status(status: str) -> List[Dict[str, Any]]:
    """Get tasks filtered by status."""
    session = get_session()
    try:
        tasks = session.query(Task).filter(Task.status == status).all()
        return [task.to_dict() for task in tasks]
    finally:
        close_session()


def get_tasks_by_priority(priority: str) -> List[Dict[str, Any]]:
    """Get tasks filtered by priority."""
    session = get_session()
    try:
        tasks = session.query(Task).filter(Task.priority == priority).all()
        return [task.to_dict() for task in tasks]
    finally:
        close_session()


def mark_task_complete(task_id: int) -> Optional[Dict[str, Any]]:
    """Mark a task as completed."""
    return update_task(task_id, {'completed': True, 'status': 'completed'})


def get_task_stats() -> Dict[str, Any]:
    """Get task statistics."""
    session = get_session()
    try:
        total = session.query(Task).count()
        completed = session.query(Task).filter(Task.completed == True).count()
        pending = session.query(Task).filter(Task.status == 'pending').count()
        in_progress = session.query(Task).filter(Task.status == 'in_progress').count()

        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'completion_rate': round(completed / total * 100, 2) if total > 0 else 0
        }
    finally:
        close_session()


# Initialize database on module import if running directly
if __name__ == '__main__':
    init_db()
    print("Database tables created successfully!")

    # Create sample tasks
    sample_tasks = [
        {'title': 'Set up CI/CD pipeline', 'priority': 'high', 'description': 'Configure GitHub Actions workflow'},
        {'title': 'Write unit tests', 'priority': 'medium', 'description': 'Add pytest tests for all endpoints'},
        {'title': 'Deploy to staging', 'priority': 'high', 'description': 'Deploy application to staging cluster'},
        {'title': 'Update documentation', 'priority': 'low', 'description': 'Update README with new features'},
    ]

    for task_data in sample_tasks:
        task = create_task(**task_data)
        print(f"Created task: {task['title']}")

    print(f"\nTotal tasks: {len(get_all_tasks())}")
