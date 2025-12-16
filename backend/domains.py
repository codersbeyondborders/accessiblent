# domains.py
import secrets
import datetime
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple

import httpx
from fastapi import HTTPException
from pydantic import BaseModel

from db import q


# Pydantic models
class DomainCreate(BaseModel):
    domain_name: str
    
    @property
    def normalized_domain_name(self) -> str:
        """Return normalized domain name."""
        return self.domain_name.strip()


class Domain(BaseModel):
    id: int
    organization_id: int
    domain_name: str
    verification_token: str
    is_verified: bool
    verification_method: Optional[str]
    verified_at: Optional[datetime.datetime]
    created_at: datetime.datetime


# Domain management functions

def generate_verification_token() -> str:
    """
    Generate a cryptographically random verification token (32 bytes).
    Returns a URL-safe base64-encoded string.
    """
    return secrets.token_urlsafe(32)


def add_domain(user_id: int, domain_name: str) -> Dict[str, Any]:
    """
    Add a new domain for the user's organization.
    Generates a unique verification token.
    
    Args:
        user_id: The ID of the user adding the domain
        domain_name: The domain name to add (e.g., "example.org")
    
    Returns:
        Dictionary containing the created domain information
    
    Raises:
        HTTPException: If user not found, domain already exists, or database error
    """
    # Normalize domain name (lowercase, strip whitespace)
    domain_name = domain_name.lower().strip()
    
    # Remove protocol if present
    if domain_name.startswith("http://") or domain_name.startswith("https://"):
        parsed = urllib.parse.urlparse(domain_name)
        domain_name = parsed.netloc or parsed.path
    
    # Remove trailing slash
    domain_name = domain_name.rstrip("/")
    
    # Validate domain name format (basic check)
    if not domain_name or "." not in domain_name:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_DOMAIN",
                "message": "Please provide a valid domain name",
                "field": "domain_name",
            }
        )
    
    # Get user's organization
    user_rows = q("SELECT organization_id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    organization_id = user_rows[0]["organization_id"]
    
    # Check if organization already has a domain (one domain per org)
    existing_any = q(
        "SELECT id, domain_name FROM domain WHERE organization_id=%s",
        (organization_id,)
    )
    if existing_any:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "DOMAIN_LIMIT_REACHED",
                "message": f"Your organization already has a domain registered: {existing_any[0]['domain_name']}. Please delete it first if you want to register a different domain.",
                "field": "domain_name",
            }
        )
    
    # Generate verification token
    verification_token = generate_verification_token()
    
    # Insert domain
    domain_id = q(
        """INSERT INTO domain (organization_id, domain_name, verification_token, 
           is_verified, created_at)
           VALUES (%s, %s, %s, %s, %s)""",
        (organization_id, domain_name, verification_token, False, datetime.datetime.utcnow())
    )
    
    # Fetch and return the created domain
    domain_rows = q("SELECT * FROM domain WHERE id=%s", (domain_id,))
    if not domain_rows:
        raise HTTPException(status_code=500, detail="Failed to create domain")
    
    return domain_rows[0]


def get_user_domains(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all domains for the user's organization.
    
    Args:
        user_id: The ID of the user
    
    Returns:
        List of domain dictionaries
    
    Raises:
        HTTPException: If user not found
    """
    # Get user's organization
    user_rows = q("SELECT organization_id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    organization_id = user_rows[0]["organization_id"]
    
    # Get all domains for this organization
    domains = q(
        """SELECT * FROM domain 
           WHERE organization_id=%s 
           ORDER BY created_at DESC""",
        (organization_id,)
    )
    
    return domains or []


def get_domain_by_id(domain_id: int, user_id: int) -> Dict[str, Any]:
    """
    Get a specific domain by ID, ensuring the user has access to it.
    
    Args:
        domain_id: The ID of the domain
        user_id: The ID of the user requesting the domain
    
    Returns:
        Domain dictionary
    
    Raises:
        HTTPException: If domain not found or user doesn't have access
    """
    # Get user's organization
    user_rows = q("SELECT organization_id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        raise HTTPException(status_code=404, detail="User not found")
    
    organization_id = user_rows[0]["organization_id"]
    
    # Get domain and verify ownership
    domain_rows = q(
        "SELECT * FROM domain WHERE id=%s AND organization_id=%s",
        (domain_id, organization_id)
    )
    
    if not domain_rows:
        raise HTTPException(
            status_code=404,
            detail="Domain not found or you don't have access to it"
        )
    
    return domain_rows[0]


def delete_domain(domain_id: int, user_id: int) -> bool:
    """
    Delete a domain, ensuring the user has access to it.
    
    Args:
        domain_id: The ID of the domain to delete
        user_id: The ID of the user requesting deletion
    
    Returns:
        True if deleted successfully
    
    Raises:
        HTTPException: If domain not found or user doesn't have access
    """
    # Verify ownership first
    get_domain_by_id(domain_id, user_id)
    
    # Delete the domain (cascade will handle related records)
    q("DELETE FROM domain WHERE id=%s", (domain_id,))
    
    return True


# Domain verification functions

async def verify_domain_meta_tag(domain: str, token: str) -> bool:
    """
    Check if the verification token exists in a meta tag on the domain's homepage.
    Looks for: <meta name="accessify-verification" content="{token}">
    
    Args:
        domain: The domain name to check
        token: The verification token to look for
    
    Returns:
        True if token found in meta tag, False otherwise
    """
    url = f"https://{domain}"
    
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": "Accessify-Verifier/1.0"}
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text
            
            # Look for the meta tag with our token
            # Format: <meta name="accessify-verification" content="TOKEN">
            meta_tag_pattern = f'<meta name="accessify-verification" content="{token}"'
            
            # Case-insensitive search
            return meta_tag_pattern.lower() in html.lower()
            
    except Exception as e:
        # Log the error but return False (verification failed)
        print(f"Meta tag verification failed for {domain}: {e}")
        return False


async def verify_domain_wellknown(domain: str, token: str) -> bool:
    """
    Check if the verification token exists in the /.well-known/accessify-verification.txt file.
    
    Args:
        domain: The domain name to check
        token: The verification token to look for
    
    Returns:
        True if token found in well-known file, False otherwise
    """
    url = f"https://{domain}/.well-known/accessify-verification.txt"
    
    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(10.0),
            headers={"User-Agent": "Accessify-Verifier/1.0"}
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text.strip()
            
            # Check if the token is in the file content
            return token in content
            
    except Exception as e:
        # Log the error but return False (verification failed)
        print(f"Well-known file verification failed for {domain}: {e}")
        return False


async def verify_domain(domain_id: int, user_id: int) -> Dict[str, Any]:
    """
    Orchestrate domain verification by checking both meta tag and well-known file.
    Updates the domain record if verification succeeds.
    
    Args:
        domain_id: The ID of the domain to verify
        user_id: The ID of the user requesting verification
    
    Returns:
        Dictionary with verification result and details
    
    Raises:
        HTTPException: If domain not found or user doesn't have access
    """
    # Get domain and verify ownership
    domain = get_domain_by_id(domain_id, user_id)
    
    # Check if already verified
    if domain["is_verified"]:
        return {
            "success": True,
            "message": "Domain is already verified",
            "method": domain["verification_method"],
            "verified_at": domain["verified_at"],
        }
    
    domain_name = domain["domain_name"]
    token = domain["verification_token"]
    
    # Try meta tag verification first
    meta_tag_found = await verify_domain_meta_tag(domain_name, token)
    
    if meta_tag_found:
        # Update domain as verified
        q(
            """UPDATE domain 
               SET is_verified=%s, verification_method=%s, verified_at=%s 
               WHERE id=%s""",
            (True, "meta_tag", datetime.datetime.utcnow(), domain_id)
        )
        
        return {
            "success": True,
            "message": "Domain verified successfully via meta tag",
            "method": "meta_tag",
            "verified_at": datetime.datetime.utcnow().isoformat(),
        }
    
    # Try well-known file verification
    wellknown_found = await verify_domain_wellknown(domain_name, token)
    
    if wellknown_found:
        # Update domain as verified
        q(
            """UPDATE domain 
               SET is_verified=%s, verification_method=%s, verified_at=%s 
               WHERE id=%s""",
            (True, "wellknown", datetime.datetime.utcnow(), domain_id)
        )
        
        return {
            "success": True,
            "message": "Domain verified successfully via well-known file",
            "method": "wellknown",
            "verified_at": datetime.datetime.utcnow().isoformat(),
        }
    
    # Verification failed
    return {
        "success": False,
        "message": "Verification failed. Please ensure the verification token is correctly placed.",
        "troubleshooting": {
            "meta_tag": "Add <meta name=\"accessify-verification\" content=\"{token}\"> to your homepage <head>",
            "wellknown": f"Create a file at https://{domain_name}/.well-known/accessify-verification.txt containing your token",
            "common_issues": [
                "Ensure the token matches exactly (case-sensitive)",
                "Check that the file or meta tag is publicly accessible",
                "Verify HTTPS is properly configured",
                "Clear any caching that might serve old content",
            ]
        }
    }


def is_domain_verified(domain_name: str, user_id: int) -> bool:
    """
    Check if a domain is verified for the user's organization.
    
    Args:
        domain_name: The domain name to check
        user_id: The ID of the user
    
    Returns:
        True if domain is verified, False otherwise
    """
    # Get user's organization
    user_rows = q("SELECT organization_id FROM user WHERE id=%s", (user_id,))
    if not user_rows:
        return False
    
    organization_id = user_rows[0]["organization_id"]
    
    # Check if domain exists and is verified
    domain_rows = q(
        """SELECT is_verified FROM domain 
           WHERE organization_id=%s AND domain_name=%s""",
        (organization_id, domain_name)
    )
    
    if not domain_rows:
        return False
    
    return domain_rows[0]["is_verified"]
