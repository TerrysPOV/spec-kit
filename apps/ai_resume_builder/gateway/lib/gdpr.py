"""
GDPR Compliance Module for AI Resume Assistant

Data Subject Rights (DSR) implementation including data export and deletion.
"""

import os
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from .models import User, Resume, ResumeRevision, UsageEvent, GDPRRequest
from .database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GDPRError(Exception):
    """Base exception for GDPR operations"""
    pass

class UserNotFoundError(GDPRError):
    """Raised when user not found for GDPR operation"""
    pass

class GDPRService:
    """
    GDPR compliance service for data export and deletion

    Implements Data Subject Rights (DSR):
    - Right of Access (data export)
    - Right to Erasure (data deletion)
    - Right to Data Portability (structured export)
    """

    def __init__(self):
        self.export_bucket_url = os.getenv("EXPORT_BUCKET_URL", "https://storage.googleapis.com/ai-resume-exports")

    async def create_gdpr_request(
        self,
        db: AsyncSession,
        user_id: str,
        request_type: str
    ) -> GDPRRequest:
        """
        Create a GDPR request record

        Args:
            db: Database session
            user_id: User's unique identifier
            request_type: "export" or "delete"

        Returns:
            Created GDPRRequest record
        """
        # Check if user exists
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Create GDPR request
        gdpr_request = GDPRRequest(
            user_id=user_id,
            request_type=request_type,
            status="pending"
        )

        db.add(gdpr_request)
        await db.flush()  # Get the ID

        logger.info(f"Created GDPR {request_type} request {gdpr_request.id} for user {user_id}")
        return gdpr_request

    async def export_user_data(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Export all user data for GDPR compliance

        Args:
            db: Database session
            user_id: User's unique identifier

        Returns:
            Complete user data export
        """
        # Get user
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        # Get all user data
        export_data = {
            "export_info": {
                "user_id": user_id,
                "exported_at": datetime.utcnow().isoformat(),
                "export_version": "1.0",
                "data_categories": ["profile", "resumes", "revisions", "usage_events"]
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            },
            "resumes": [],
            "revisions": [],
            "usage_events": []
        }

        # Get resumes
        result = await db.execute(
            select(Resume).where(Resume.user_id == user_id).order_by(desc(Resume.created_at))
        )
        resumes = result.scalars().all()

        for resume in resumes:
            resume_data = {
                "id": resume.id,
                "title": resume.title,
                "content_json": resume.content_json,
                "original_filename": resume.original_filename,
                "created_at": resume.created_at.isoformat() if resume.created_at else None,
                "updated_at": resume.updated_at.isoformat() if resume.updated_at else None
            }
            export_data["resumes"].append(resume_data)

            # Get revisions for this resume
            result = await db.execute(
                select(ResumeRevision)
                .where(ResumeRevision.resume_id == resume.id)
                .order_by(desc(ResumeRevision.created_at))
            )
            revisions = result.scalars().all()

            for revision in revisions:
                revision_data = {
                    "id": revision.id,
                    "resume_id": revision.resume_id,
                    "revision_number": revision.revision_number,
                    "diff_json": revision.diff_json,
                    "change_description": revision.change_description,
                    "created_at": revision.created_at.isoformat() if revision.created_at else None
                }
                export_data["revisions"].append(revision_data)

        # Get usage events
        result = await db.execute(
            select(UsageEvent)
            .where(UsageEvent.user_id == user_id)
            .order_by(desc(UsageEvent.created_at))
        )
        usage_events = result.scalars().all()

        for event in usage_events:
            event_data = {
                "id": event.id,
                "model": event.model,
                "prompt_tokens": event.prompt_tokens,
                "completion_tokens": event.completion_tokens,
                "total_tokens": event.total_tokens,
                "cost_usd": event.cost_usd,
                "status": event.status,
                "error_message": event.error_message,
                "request_id": event.request_id,
                "endpoint": event.endpoint,
                "metadata": event.metadata,
                "created_at": event.created_at.isoformat() if event.created_at else None
            }
            export_data["usage_events"].append(event_data)

        logger.info(f"Exported data for user {user_id}: {len(export_data['resumes'])} resumes, {len(export_data['usage_events'])} usage events")
        return export_data

    async def delete_user_data(
        self,
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Delete all user data for GDPR compliance

        Args:
            db: Database session
            user_id: User's unique identifier

        Returns:
            Deletion summary
        """
        # Check if user exists
        user = await db.get(User, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        deletion_summary = {
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted_records": {
                "resumes": 0,
                "revisions": 0,
                "usage_events": 0,
                "rate_limits": 0,
                "gdpr_requests": 0
            }
        }

        # Count records before deletion for reporting
        from sqlalchemy import func

        # Count resumes
        result = await db.execute(
            select(func.count()).select_from(Resume).where(Resume.user_id == user_id)
        )
        deletion_summary["deleted_records"]["resumes"] = result.scalar()

        # Count revisions
        result = await db.execute(
            select(func.count()).select_from(ResumeRevision)
            .join(Resume)
            .where(Resume.user_id == user_id)
        )
        deletion_summary["deleted_records"]["revisions"] = result.scalar()

        # Count usage events
        result = await db.execute(
            select(func.count()).select_from(UsageEvent).where(UsageEvent.user_id == user_id)
        )
        deletion_summary["deleted_records"]["usage_events"] = result.scalar()

        # Delete in order (respecting foreign key constraints)
        # Delete revisions first (they reference resumes)
        await db.execute(
            ResumeRevision.__table__.delete().where(
                ResumeRevision.resume_id.in_(
                    select(Resume.id).where(Resume.user_id == user_id)
                )
            )
        )

        # Delete resumes
        await db.execute(
            Resume.__table__.delete().where(Resume.user_id == user_id)
        )

        # Delete usage events
        await db.execute(
            UsageEvent.__table__.delete().where(UsageEvent.user_id == user_id)
        )

        # Delete rate limits
        from .models import RateLimit
        await db.execute(
            RateLimit.__table__.delete().where(RateLimit.user_id == user_id)
        )

        # Delete GDPR requests (except the current one)
        await db.execute(
            GDPRRequest.__table__.delete().where(GDPRRequest.user_id == user_id)
        )

        # Finally delete the user
        await db.delete(user)

        logger.warning(f"Deleted all data for user {user_id}")
        return deletion_summary

    async def get_user_gdpr_requests(
        self,
        db: AsyncSession,
        user_id: str
    ) -> List[GDPRRequest]:
        """
        Get GDPR request history for user

        Args:
            db: Database session
            user_id: User's unique identifier

        Returns:
            List of GDPR requests for the user
        """
        result = await db.execute(
            select(GDPRRequest)
            .where(GDPRRequest.user_id == user_id)
            .order_by(desc(GDPRRequest.requested_at))
        )

        return result.scalars().all()

# Global GDPR service instance
_gdpr_service: Optional[GDPRError] = None

def get_gdpr_service() -> GDPRService:
    """Get or create global GDPR service instance"""
    global _gdpr_service
    if _gdpr_service is None:
        _gdpr_service = GDPRService()
    return _gdpr_service

# Utility functions for data export formatting
def format_export_for_download(export_data: Dict[str, Any]) -> str:
    """
    Format export data as JSON for download

    Args:
        export_data: Raw export data

    Returns:
        Formatted JSON string
    """
    return json.dumps(export_data, indent=2, default=str, ensure_ascii=False)

def generate_export_filename(user_id: str) -> str:
    """
    Generate filename for data export

    Args:
        user_id: User's unique identifier

    Returns:
        Export filename with timestamp
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    return f"ai_resume_data_export_{user_id}_{timestamp}.json"