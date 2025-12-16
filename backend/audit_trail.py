# audit_trail.py
import datetime
import json
from typing import Optional, Dict, Any, List

from db import q


def log_event(
    event_type: str,
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> int:
    """
    Log a generic event to the audit trail.
    
    Args:
        event_type: Type of event (e.g., 'login', 'domain_verification', 'remediation')
        user_id: ID of the user performing the action (optional)
        organization_id: ID of the organization (optional, will be fetched from user if not provided)
        details: Dictionary containing event-specific details (will be stored as JSON)
        ip_address: IP address of the user (optional)
    
    Returns:
        The ID of the created audit log entry
    """
    # If user_id is provided but organization_id is not, fetch it
    if user_id and not organization_id:
        user_rows = q("SELECT organization_id FROM user WHERE id=%s", (user_id,))
        if user_rows:
            organization_id = user_rows[0]["organization_id"]
    
    # Convert details dict to JSON string
    details_json = json.dumps(details) if details else None
    
    # Insert audit log entry
    audit_id = q(
        """INSERT INTO audit_log (event_type, user_id, organization_id, details, ip_address, created_at)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (event_type, user_id, organization_id, details_json, ip_address, datetime.datetime.utcnow())
    )
    
    return audit_id


def log_agreement_acceptance(
    user_id: int,
    agreement_version: str,
    ip_address: Optional[str] = None
) -> int:
    """
    Log an ethics agreement acceptance to the audit trail.
    
    Args:
        user_id: ID of the user accepting the agreement
        agreement_version: Version of the agreement being accepted
        ip_address: IP address of the user (optional)
    
    Returns:
        The ID of the created audit log entry
    """
    details = {
        "event": "ethics_agreement_accepted",
        "agreement_version": agreement_version,
        "user_id": user_id,
    }
    
    return log_event(
        event_type="ethics_acceptance",
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )


def log_domain_verification(
    user_id: int,
    domain_id: int,
    domain_name: str,
    verification_method: str,
    success: bool,
    ip_address: Optional[str] = None
) -> int:
    """
    Log a domain verification attempt to the audit trail.
    
    Args:
        user_id: ID of the user performing the verification
        domain_id: ID of the domain being verified
        domain_name: Name of the domain (e.g., 'example.org')
        verification_method: Method used ('meta_tag' or 'well_known')
        success: Whether the verification was successful
        ip_address: IP address of the user (optional)
    
    Returns:
        The ID of the created audit log entry
    """
    details = {
        "event": "domain_verification_attempt",
        "domain_id": domain_id,
        "domain_name": domain_name,
        "verification_method": verification_method,
        "success": success,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    
    event_type = "domain_verification_success" if success else "domain_verification_failure"
    
    return log_event(
        event_type=event_type,
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )


def log_remediation(
    user_id: int,
    website_id: int,
    entry_url: str,
    issues_found: int,
    issues_fixed: int,
    page_id: Optional[int] = None,
    ip_address: Optional[str] = None
) -> int:
    """
    Log a remediation event to the audit trail.
    
    Args:
        user_id: ID of the user performing the remediation
        website_id: ID of the website being remediated
        entry_url: The entry URL that was remediated
        issues_found: Number of accessibility issues found
        issues_fixed: Number of accessibility issues fixed
        page_id: ID of the created page record (optional)
        ip_address: IP address of the user (optional)
    
    Returns:
        The ID of the created audit log entry
    """
    details = {
        "event": "remediation_completed",
        "website_id": website_id,
        "entry_url": entry_url,
        "issues_found": issues_found,
        "issues_fixed": issues_fixed,
        "page_id": page_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }
    
    return log_event(
        event_type="remediation",
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )


def query_audit_trail(
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Query the audit trail with optional filters.
    
    Args:
        user_id: Filter by user ID (optional)
        organization_id: Filter by organization ID (optional)
        event_type: Filter by event type (optional)
        start_date: Filter by start date (inclusive, optional)
        end_date: Filter by end date (inclusive, optional)
        limit: Maximum number of records to return (default 100)
        offset: Number of records to skip (default 0)
    
    Returns:
        List of audit log records matching the filters, ordered by created_at DESC
    """
    # Build the WHERE clause dynamically
    where_clauses = []
    params = []
    
    if user_id is not None:
        where_clauses.append("user_id = %s")
        params.append(user_id)
    
    if organization_id is not None:
        where_clauses.append("organization_id = %s")
        params.append(organization_id)
    
    if event_type is not None:
        where_clauses.append("event_type = %s")
        params.append(event_type)
    
    if start_date is not None:
        where_clauses.append("created_at >= %s")
        params.append(start_date)
    
    if end_date is not None:
        where_clauses.append("created_at <= %s")
        params.append(end_date)
    
    # Construct the SQL query
    sql = "SELECT * FROM audit_log"
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    sql += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])
    
    # Execute query
    audit_rows = q(sql, tuple(params))
    
    # Parse JSON details field for each row
    for row in audit_rows:
        if row.get("details") and isinstance(row["details"], str):
            try:
                row["details"] = json.loads(row["details"])
            except json.JSONDecodeError:
                # If JSON parsing fails, leave as string
                pass
    
    return audit_rows or []


def get_user_audit_history(
    user_id: int,
    event_types: Optional[List[str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get audit history for a specific user, optionally filtered by event types.
    
    Args:
        user_id: ID of the user
        event_types: List of event types to filter by (optional)
        limit: Maximum number of records to return (default 50)
    
    Returns:
        List of audit log records for the user
    """
    if event_types:
        # Build IN clause for event types
        placeholders = ", ".join(["%s"] * len(event_types))
        sql = f"""SELECT * FROM audit_log 
                  WHERE user_id = %s AND event_type IN ({placeholders})
                  ORDER BY created_at DESC LIMIT %s"""
        params = [user_id] + event_types + [limit]
    else:
        sql = """SELECT * FROM audit_log 
                 WHERE user_id = %s 
                 ORDER BY created_at DESC LIMIT %s"""
        params = [user_id, limit]
    
    audit_rows = q(sql, tuple(params))
    
    # Parse JSON details field
    for row in audit_rows:
        if row.get("details") and isinstance(row["details"], str):
            try:
                row["details"] = json.loads(row["details"])
            except json.JSONDecodeError:
                pass
    
    return audit_rows or []


def get_organization_audit_history(
    organization_id: int,
    event_types: Optional[List[str]] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get audit history for an entire organization, optionally filtered by event types.
    
    Args:
        organization_id: ID of the organization
        event_types: List of event types to filter by (optional)
        limit: Maximum number of records to return (default 100)
    
    Returns:
        List of audit log records for the organization
    """
    if event_types:
        placeholders = ", ".join(["%s"] * len(event_types))
        sql = f"""SELECT * FROM audit_log 
                  WHERE organization_id = %s AND event_type IN ({placeholders})
                  ORDER BY created_at DESC LIMIT %s"""
        params = [organization_id] + event_types + [limit]
    else:
        sql = """SELECT * FROM audit_log 
                 WHERE organization_id = %s 
                 ORDER BY created_at DESC LIMIT %s"""
        params = [organization_id, limit]
    
    audit_rows = q(sql, tuple(params))
    
    # Parse JSON details field
    for row in audit_rows:
        if row.get("details") and isinstance(row["details"], str):
            try:
                row["details"] = json.loads(row["details"])
            except json.JSONDecodeError:
                pass
    
    return audit_rows or []


def count_audit_events(
    user_id: Optional[int] = None,
    organization_id: Optional[int] = None,
    event_type: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None
) -> int:
    """
    Count audit events matching the given filters.
    
    Args:
        user_id: Filter by user ID (optional)
        organization_id: Filter by organization ID (optional)
        event_type: Filter by event type (optional)
        start_date: Filter by start date (inclusive, optional)
        end_date: Filter by end date (inclusive, optional)
    
    Returns:
        Count of matching audit log records
    """
    where_clauses = []
    params = []
    
    if user_id is not None:
        where_clauses.append("user_id = %s")
        params.append(user_id)
    
    if organization_id is not None:
        where_clauses.append("organization_id = %s")
        params.append(organization_id)
    
    if event_type is not None:
        where_clauses.append("event_type = %s")
        params.append(event_type)
    
    if start_date is not None:
        where_clauses.append("created_at >= %s")
        params.append(start_date)
    
    if end_date is not None:
        where_clauses.append("created_at <= %s")
        params.append(end_date)
    
    sql = "SELECT COUNT(*) as count FROM audit_log"
    
    if where_clauses:
        sql += " WHERE " + " AND ".join(where_clauses)
    
    result = q(sql, tuple(params) if params else None)
    
    return result[0]["count"] if result else 0
