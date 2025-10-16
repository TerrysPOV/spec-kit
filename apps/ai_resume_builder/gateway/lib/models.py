"""
Database Models for AI Resume Assistant

SQLAlchemy models for user management, resume storage, usage tracking, and GDPR compliance.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication and data ownership"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    usage_events = relationship("UsageEvent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"

class Resume(Base):
    """Resume model for storing user resumes"""
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    content_json = Column(JSON, nullable=False)  # Parsed resume data
    original_filename = Column(String)  # Original uploaded file name
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="resumes")
    revisions = relationship("ResumeRevision", back_populates="resume", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Resume(id='{self.id}', title='{self.title}', user_id='{self.user_id}')>"

class ResumeRevision(Base):
    """Resume revision history for tracking changes"""
    __tablename__ = "resume_revisions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    diff_json = Column(JSON, nullable=False)  # Changes made in this revision
    change_description = Column(Text)  # Human-readable description of changes
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = relationship("Resume", back_populates="revisions")

    def __repr__(self):
        return f"<ResumeRevision(id='{self.id}', resume_id='{self.resume_id}', revision={self.revision_number})>"

class UsageEvent(Base):
    """Usage tracking for OpenRouter API calls and costs"""
    __tablename__ = "usage_events"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    model = Column(String, nullable=False)  # AI model used (e.g., "anthropic/claude-3.5-sonnet")
    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)
    cost_usd = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False)  # "success", "error", "rate_limited"
    error_message = Column(Text)  # Error details if status is "error"
    request_id = Column(String)  # OpenRouter request ID for tracing
    endpoint = Column(String)  # API endpoint used (e.g., "/v1/apply", "/v1/generate")
    metadata = Column(JSON)  # Additional context (e.g., {"company_domain": "example.com"})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="usage_events")

    def __repr__(self):
        return f"<UsageEvent(id='{self.id}', user_id='{self.user_id}', model='{self.model}', cost=${self.cost_usd".4f"})>"

class RateLimit(Base):
    """Rate limiting state for users"""
    __tablename__ = "rate_limits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    request_count = Column(Integer, nullable=False, default=0)
    window_start = Column(DateTime(timezone=True), server_default=func.now())
    monthly_cost_usd = Column(Float, nullable=False, default=0.0)
    month_start = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="rate_limit")

    def __repr__(self):
        return f"<RateLimit(user_id='{self.user_id}', requests={self.request_count}, cost=${self.monthly_cost_usd".2f"})>"

class GDPRRequest(Base):
    """GDPR Data Subject Request logging"""
    __tablename__ = "gdpr_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    request_type = Column(String, nullable=False)  # "export", "delete", "rectify"
    status = Column(String, nullable=False, default="pending")  # "pending", "processing", "completed", "failed"
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    download_url = Column(String)  # For export requests
    error_message = Column(Text)  # For failed requests

    # Relationships
    user = relationship("User", back_populates="gdpr_requests")

    def __repr__(self):
        return f"<GDPRRequest(id='{self.id}', user_id='{self.user_id}', type='{self.request_type}', status='{self.status}')>"

# Add relationships to User model
User.rate_limit = relationship("RateLimit", back_populates="user", uselist=False, cascade="all, delete-orphan")
User.gdpr_requests = relationship("GDPRRequest", back_populates="user", cascade="all, delete-orphan")

# Database helper functions
def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """Drop all tables (for testing)"""
    Base.metadata.drop_all(bind=engine)