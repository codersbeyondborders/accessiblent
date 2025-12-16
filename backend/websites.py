# websites.py
import datetime
import urllib.parse
from typing import List, Dict, Any, Optional

from fastapi import HTTPException
from pydantic import BaseModel, HttpUrl

from db import q
from domains import is_domain_verified


# Pydantic models
class WebsiteCreate(BaseModel):
    entry_url: str
    domain_id: int
    name: Optional[str] = None


class Website(BaseModel):
    id: int
    user_id: int
    domain_id: int
    entry_url: str
    name: Optional[str]
    status: str
    last_remediation_at: Optional[datetime.datetime]
    created_at: datetime.datetime


# Website management functions

def validate_url_domain(url: str, domain: str) -> bool:
    """
    Check if a URL belongs to the specified domain.
    
    Args:
        url: The full URL to validate (e.g., "https://example.org/page")
        domain: The domain name to check against (e.g., "example.org")
    
    Returns:
        True if URL domain matches, False otherwise
    """
    try:
        # Parse the URL
        parsed = urllib.parse.urlparse(url)
        
        # Extract the domain from the URL
        url_domain = parsed.netloc.lower().strip()
        
        # Remove www. prefix if present for comparison
        if url_domain.startswith("www."):
            url_domain = url_domain[4:]
        
        domain_normalized = domain.lower().strip()
        if domain_normalized.startswith("www."):
            domain_normalized = domain_normalized[4:]
        
        # Check if domains match
        return url_domain == domain_normalized
        
    except Exception:
        return False


def register_website(user_id: int, entry_url: str, domain_id: int, name: Optional[str] = None) -> Dict[str, Any]:
    """
    Register a new website for remediation.
    Validates that the URL domain matches a verified domain owned by the user.
    
    Args:
        user_id: The ID of the user registering the website
        entry_url: The starting URL for the website
        domain_id: The ID of the verified domain
        name: Optional friendly name for the website
    
    Returns:
        Dictionary containing the created website information
    
    Raises:
        HTTPException: If validation fails or domain not verified
    """
    # Validate URL format
    if not entry_url or not entry_url.strip():
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_URL",
                "message": "Please provide a valid entry URL",
                "field": "entry_url",
            }
        )
    
    entry_url = entry_url.strip()
    
    # Ensure URL has a scheme
    if not entry_url.startswith("http://") and not entry_url.startswith("https://"):
        entry_url = "https://" + entry_url
    
    # Validate URL can be parsed
    try:
        parsed = urllib.parse.urlparse(entry_url)
        if not parsed.netloc:
            raise ValueError("No domain in URL")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_URL",
                "message": "Please provide a valid URL with a domain",
                "field": "entry_url",
            }
        )
    
    # Get user's organization
    user_rows = q("SELECT organization_id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    organization_id = user_rows[0]["organization_id"]
    
    # Get the domain and verify ownership
    domain_rows = q(
        """SELECT id, domain_name, is_verified, organization_id 
           FROM domain 
           WHERE id=%s""",
        (domain_id,)
    )
    
    if not domain_rows:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "DOMAIN_NOT_FOUND",
                "message": "Domain not found",
                "field": "domain_id",
            }
        )
    
    domain = domain_rows[0]
    
    # Verify user owns the domain (same organization)
    if domain["organization_id"] != organization_id:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "DOMAIN_NOT_OWNED",
                "message": "You don't have access to this domain",
                "field": "domain_id",
            }
        )
    
    # Check if domain is verified
    if not domain["is_verified"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "DOMAIN_NOT_VERIFIED",
                "message": "Domain must be verified before registering a website",
                "field": "domain_id",
            }
        )
    
    # Validate that the URL domain matches the verified domain
    if not validate_url_domain(entry_url, domain["domain_name"]):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "URL_DOMAIN_MISMATCH",
                "message": f"Entry URL must belong to the domain {domain['domain_name']}",
                "field": "entry_url",
                "expected_domain": domain["domain_name"],
            }
        )
    
    # Allow multiple websites per domain (removed one-website-per-org limit)
    
    # Create the website record
    website_id = q(
        """INSERT INTO website (user_id, domain_id, entry_url, name, status, created_at)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, domain_id, entry_url, name, "registered", datetime.datetime.utcnow())
    )
    
    # Fetch and return the created website
    website_rows = q("SELECT * FROM website WHERE id=%s", (website_id,))
    if not website_rows:
        raise HTTPException(status_code=500, detail="Failed to create website")
    
    return website_rows[0]


def get_user_websites(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all websites registered by the user.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        List of website dictionaries with domain information
    
    Raises:
        HTTPException: If user not found
    """
    # Verify user exists
    user_rows = q("SELECT id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all websites for this user with domain information
    websites = q(
        """SELECT 
               w.*,
               d.domain_name,
               d.is_verified as domain_verified
           FROM website w
           JOIN domain d ON w.domain_id = d.id
           WHERE w.user_id=%s 
           ORDER BY w.created_at DESC""",
        (user_id,)
    )
    
    return websites or []


def get_website_details(website_id: int, user_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific website.
    Ensures the user has access to the website.
    
    Args:
        website_id: The ID of the website
        user_id: The ID of the user requesting the details
    
    Returns:
        Dictionary containing website details with domain information
    
    Raises:
        HTTPException: If website not found or user doesn't have access
    """
    # Get website with domain information
    website_rows = q(
        """SELECT 
               w.*,
               d.domain_name,
               d.is_verified as domain_verified,
               d.organization_id
           FROM website w
           JOIN domain d ON w.domain_id = d.id
           WHERE w.id=%s""",
        (website_id,)
    )
    
    if not website_rows:
        raise HTTPException(
            status_code=404,
            detail="Website not found"
        )
    
    website = website_rows[0]
    
    # Verify user owns the website
    if website["user_id"] != user_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this website"
        )
    
    return website


def delete_website(website_id: int, user_id: int) -> bool:
    """
    Delete a website, ensuring the user has access to it.
    
    Args:
        website_id: The ID of the website to delete
        user_id: The ID of the user requesting deletion
    
    Returns:
        True if deleted successfully
    
    Raises:
        HTTPException: If website not found or user doesn't have access
    """
    # Verify ownership first
    get_website_details(website_id, user_id)
    
    # Delete the website (cascade will handle related records)
    q("DELETE FROM website WHERE id=%s", (website_id,))
    
    return True
