# ethics.py
import datetime
import json
from typing import Optional, Dict, Any, List

from fastapi import HTTPException
from pydantic import BaseModel

from db import q


# Pydantic models
class EthicsAgreement(BaseModel):
    version: str
    content: str
    effective_date: datetime.datetime


class EthicsAcceptance(BaseModel):
    agreement_version: str
    ip_address: Optional[str] = None


class EthicsAcceptanceRecord(BaseModel):
    id: int
    user_id: int
    agreement_version: str
    accepted_at: datetime.datetime
    ip_address: Optional[str]


# Ethics agreement management functions

def get_current_agreement() -> Dict[str, Any]:
    """
    Fetch the latest version of the ethics agreement.
    
    Returns:
        Dictionary containing the current agreement version, content, and effective date
    
    Raises:
        HTTPException: If no agreement exists in the database
    """
    # Get the most recent agreement by effective_date
    agreement_rows = q(
        """SELECT version, content, effective_date, created_at 
           FROM ethics_agreement 
           ORDER BY effective_date DESC, created_at DESC 
           LIMIT 1"""
    )
    
    if not agreement_rows:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "NO_AGREEMENT",
                "message": "No ethics agreement found in the system",
            }
        )
    
    return agreement_rows[0]


def has_accepted_current_version(user_id: int) -> bool:
    """
    Check if a user has accepted the current version of the ethics agreement.
    
    Args:
        user_id: The ID of the user to check
    
    Returns:
        True if user has accepted the current version, False otherwise
    """
    # Get current agreement version
    try:
        current_agreement = get_current_agreement()
    except HTTPException:
        # No agreement exists, so no acceptance required
        return True
    
    current_version = current_agreement["version"]
    
    # Check if user has accepted this version
    acceptance_rows = q(
        """SELECT id FROM ethics_acceptance 
           WHERE user_id=%s AND agreement_version=%s""",
        (user_id, current_version)
    )
    
    return bool(acceptance_rows)


def record_acceptance(user_id: int, version: str, ip_address: Optional[str] = None) -> Dict[str, Any]:
    """
    Record a user's acceptance of an ethics agreement version.
    Creates an audit trail entry.
    
    Args:
        user_id: The ID of the user accepting the agreement
        version: The version of the agreement being accepted
        ip_address: The IP address of the user (optional)
    
    Returns:
        Dictionary containing the acceptance record
    
    Raises:
        HTTPException: If the agreement version doesn't exist or user not found
    """
    # Verify the agreement version exists
    agreement_rows = q(
        "SELECT version FROM ethics_agreement WHERE version=%s",
        (version,)
    )
    
    if not agreement_rows:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "AGREEMENT_NOT_FOUND",
                "message": f"Ethics agreement version {version} not found",
            }
        )
    
    # Verify user exists
    user_rows = q("SELECT id, organization_id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    organization_id = user_rows[0]["organization_id"]
    
    # Check if user has already accepted this version
    existing_acceptance = q(
        """SELECT id FROM ethics_acceptance 
           WHERE user_id=%s AND agreement_version=%s""",
        (user_id, version)
    )
    
    if existing_acceptance:
        # Already accepted, return existing record
        acceptance_id = existing_acceptance[0]["id"]
    else:
        # Record the acceptance
        acceptance_id = q(
            """INSERT INTO ethics_acceptance (user_id, agreement_version, accepted_at, ip_address)
               VALUES (%s, %s, %s, %s)""",
            (user_id, version, datetime.datetime.utcnow(), ip_address)
        )
    
    # Create audit trail entry
    audit_details = {
        "event": "ethics_agreement_accepted",
        "agreement_version": version,
        "user_id": user_id,
        "ip_address": ip_address,
    }
    
    q(
        """INSERT INTO audit_log (event_type, user_id, organization_id, details, ip_address, created_at)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        ("ethics_acceptance", user_id, organization_id, 
         json.dumps(audit_details), ip_address, datetime.datetime.utcnow())
    )
    
    # Fetch and return the acceptance record
    acceptance_rows = q(
        "SELECT * FROM ethics_acceptance WHERE id=%s",
        (acceptance_id,)
    )
    
    return acceptance_rows[0] if acceptance_rows else {}


def get_acceptance_history(user_id: int) -> List[Dict[str, Any]]:
    """
    Get the history of ethics agreement acceptances for a user.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        List of acceptance records ordered by acceptance date (most recent first)
    """
    acceptance_rows = q(
        """SELECT * FROM ethics_acceptance 
           WHERE user_id=%s 
           ORDER BY accepted_at DESC""",
        (user_id,)
    )
    
    return acceptance_rows or []


def get_acceptance_status(user_id: int) -> Dict[str, Any]:
    """
    Get the user's current acceptance status including whether they need to accept.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        Dictionary with current agreement info and user's acceptance status
    """
    try:
        current_agreement = get_current_agreement()
    except HTTPException:
        return {
            "has_agreement": False,
            "needs_acceptance": False,
            "message": "No ethics agreement configured",
        }
    
    has_accepted = has_accepted_current_version(user_id)
    
    return {
        "has_agreement": True,
        "current_version": current_agreement["version"],
        "effective_date": current_agreement["effective_date"],
        "has_accepted": has_accepted,
        "needs_acceptance": not has_accepted,
    }


def require_ethics_acceptance(user_id: int) -> None:
    """
    Middleware-style function to check if user has accepted current ethics agreement.
    Raises HTTPException if not accepted.
    
    Args:
        user_id: The ID of the user to check
    
    Raises:
        HTTPException: If user has not accepted the current ethics agreement
    """
    if not has_accepted_current_version(user_id):
        try:
            current_agreement = get_current_agreement()
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "ETHICS_ACCEPTANCE_REQUIRED",
                    "message": "You must accept the current ethics agreement before performing this action",
                    "current_version": current_agreement["version"],
                }
            )
        except HTTPException as e:
            if e.status_code == 500:
                # No agreement exists, allow action
                return
            raise
