# app.py
import os
import json
import datetime
import urllib.parse

import httpx
from fastapi import FastAPI, HTTPException, Query, Body, Depends, Response, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from db import init_pool, q
from a11y import extract_chunks, audit
from fixer import apply_fixes
from auth import (
    UserCreate, UserLogin, User,
    is_public_email_domain, hash_password, verify_password,
    create_jwt_token, verify_jwt_token, get_current_user, get_current_user_optional,
    create_verification_token, VERIFICATION_TOKEN_EXPIRATION_DAYS
)
from email_service import send_verification_email, send_welcome_email
from domains import (
    DomainCreate, Domain,
    add_domain, get_user_domains, get_domain_by_id,
    delete_domain, verify_domain
)
from ethics import (
    EthicsAgreement, EthicsAcceptance,
    get_current_agreement, has_accepted_current_version,
    record_acceptance, get_acceptance_history, get_acceptance_status,
    require_ethics_acceptance
)
from websites import (
    WebsiteCreate, Website,
    register_website, get_user_websites, get_website_details,
    delete_website
)

from typing import List, Optional, Dict, Any

# ---------- env & init ----------
load_dotenv()
init_pool()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")  # 1536 dims (OpenAI)
CHAT_MODEL  = os.getenv("CHAT_MODEL",  "gpt-4o-mini")

try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except Exception:
    openai_client = None  # run without LLM if SDK missing

app = FastAPI(title="A11y Agent – One-Click Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:4173",  # Vite preview
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for accessibility toolbar
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------- helpers ----------
async def fetch_html(url: str) -> str:
    # Lower DNS/connect/read timeouts to fail fast on slow sites
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=httpx.Timeout(10.0, connect=5.0, read=10.0),
        limits=limits,
        headers={"User-Agent": "a11y-agent/1.0"}
    ) as s:
        r = await s.get(url)
        r.raise_for_status()
        return r.text


def ensure_dict(val):
    if isinstance(val, dict): return val
    if not val: return {}
    if isinstance(val, str):
        try: return json.loads(val)
        except Exception: return {}
    return {}

def embed_text(text: str):
    """Return a list[float] embedding or None if unavailable."""
    if not openai_client: 
        return None
    t = (text or "").strip()
    if not t:
        return None
    r = openai_client.embeddings.create(model=EMBED_MODEL, input=t[:4000])
    return r.data[0].embedding  # 1536 floats

def llm_summary_from_text(text: str) -> str:
    """Short, accessible summary for visually impaired users."""
    if not openai_client:
        return ""
    ctx = (text or "")[:8000]
    prompt = (
        "Summarize the page for a visually impaired reader in 4–6 clear bullets. "
        "Be concise and factual.\n\nCONTENT:\n" + ctx
    )
    r = openai_client.responses.create(
        model=CHAT_MODEL,
        input=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_output_tokens=250,
    )
    return (r.output_text or "").strip()

def _prep_text_for_embedding(t: str, limit: int = 2000) -> str:
    t = (t or "").strip()
    return t[:limit] if len(t) > limit else t

def embed_texts_batched(texts: List[str]) -> List[Optional[List[float]]]:
    """
    Embed a list of texts in one API call.
    Returns a list of vectors (list[float]) or None where unavailable.
    """
    if not openai_client or not texts:
        return [None] * len(texts)
    inputs = [_prep_text_for_embedding(t) for t in texts]
    resp = openai_client.embeddings.create(model=EMBED_MODEL, input=inputs)
    # resp.data order matches inputs
    return [item.embedding for item in resp.data]

def select_chunks_for_embedding(db_chunks: List[dict], k: int = 64) -> List[dict]:
    """
    Keep only 'section' and 'heading'; prefer longer text; take top-k.
    """
    candidates: List[tuple] = []
    for r in db_chunks:
        role = (r.get("role") or "").lower()
        if role in ("section", "heading"):
            txt = (r.get("text") or "").strip()
            if txt and len(txt) >= 60:  # skip tiny fragments
                candidates.append((len(txt), r))
    candidates.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in candidates[:k]]


def generate_preview_url(page_id: int, base_url: Optional[str] = None) -> str:
    """
    Generate a unique preview URL for a remediated page.
    
    Args:
        page_id: The ID of the page
        base_url: Optional base URL (defaults to environment or localhost)
    
    Returns:
        Full preview URL
    """
    if base_url is None:
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Remove trailing slash if present
    base_url = base_url.rstrip("/")
    
    return f"{base_url}/output/{page_id}"


def generate_iframe_snippet(preview_url: str, domain: str, width: str = "100%", height: str = "600px") -> str:
    """
    Generate an iframe snippet for embedding remediated content.
    
    Args:
        preview_url: The preview URL to embed
        domain: The verified domain (for title/description)
        width: Width of the iframe (default: 100%)
        height: Height of the iframe (default: 600px)
    
    Returns:
        HTML iframe snippet with sandbox attributes
    """
    snippet = f'''<iframe 
    src="{preview_url}" 
    width="{width}" 
    height="{height}"
    sandbox="allow-same-origin allow-forms allow-scripts"
    title="Accessible version of {domain}"
    style="border: 1px solid #ccc; border-radius: 4px;"
    loading="lazy">
</iframe>'''
    
    return snippet



# ---------- routes ----------

# ========== Authentication Endpoints ==========

@app.post("/api/auth/signup")
async def signup(user_data: UserCreate):
    """
    Register a new user with organization email validation.
    Creates organization if it doesn't exist, sends verification email.
    """
    # Validate email domain is not public
    if is_public_email_domain(user_data.email):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_EMAIL_DOMAIN",
                "message": "Please use your organization email address",
                "field": "email",
            }
        )
    
    # Check if email already exists
    existing_user = q("SELECT id FROM user WHERE email=%s", (user_data.email,))
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "EMAIL_EXISTS",
                "message": "An account with this email already exists",
                "field": "email",
            }
        )
    
    # Extract domain from email
    email_domain = user_data.email.split("@")[-1].lower().strip()
    
    # Check if organization exists, create if not
    org_rows = q("SELECT id FROM organization WHERE email_domain=%s", (email_domain,))
    if org_rows:
        organization_id = org_rows[0]["id"]
    else:
        organization_id = q(
            "INSERT INTO organization (name, email_domain) VALUES (%s, %s)",
            (user_data.organization_name, email_domain)
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Generate verification token
    verification_token = create_verification_token()
    token_expires = datetime.datetime.utcnow() + datetime.timedelta(days=VERIFICATION_TOKEN_EXPIRATION_DAYS)
    
    # Create user
    user_id = q(
        """INSERT INTO user (organization_id, email, password_hash, full_name, 
           is_verified, verification_token, verification_token_expires)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (organization_id, user_data.email, password_hash, user_data.full_name,
         False, verification_token, token_expires)
    )
    
    # Send verification email
    try:
        await send_verification_email(user_data.email, verification_token, user_data.full_name)
    except Exception as e:
        # Log error but don't fail signup - user can request new verification email
        print(f"Failed to send verification email: {e}")
    
    return {
        "message": "Account created successfully. Please check your email to verify your account.",
        "user_id": user_id,
    }


@app.post("/api/auth/verify-email/{token}")
async def verify_email(token: str):
    """
    Verify user email with the provided token.
    Activates the account if token is valid and not expired.
    """
    # Find user with this verification token
    user_rows = q(
        """SELECT id, is_verified, verification_token_expires 
           FROM user WHERE verification_token=%s""",
        (token,)
    )
    
    if not user_rows:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid or expired verification token",
            }
        )
    
    user = user_rows[0]
    
    # Check if already verified
    if user["is_verified"]:
        return {"message": "Email already verified. You can now log in."}
    
    # Check if token expired
    if user["verification_token_expires"] < datetime.datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail={
                "code": "TOKEN_EXPIRED",
                "message": "Verification token has expired. Please request a new one.",
            }
        )
    
    # Activate account
    q(
        """UPDATE user SET is_verified=%s, verification_token=%s, 
           verification_token_expires=%s WHERE id=%s""",
        (True, None, None, user["id"])
    )
    
    # Fetch user details for welcome email
    user_details = q(
        """SELECT u.email, u.full_name, o.name as organization_name
           FROM user u
           JOIN organization o ON u.organization_id = o.id
           WHERE u.id = %s""",
        (user["id"],)
    )
    
    if user_details:
        user_info = user_details[0]
        # Send welcome email
        try:
            await send_welcome_email(
                user_info["email"],
                user_info["full_name"],
                user_info["organization_name"]
            )
        except Exception as e:
            # Log error but don't fail verification
            print(f"Failed to send welcome email: {e}")
    
    return {"message": "Email verified successfully. You can now log in."}


@app.post("/api/auth/login")
async def login(credentials: UserLogin, response: Response):
    """
    Authenticate user and create session.
    Returns JWT token in HTTP-only cookie.
    """
    # Find user by email
    user_rows = q("SELECT * FROM user WHERE email=%s", (credentials.email,))
    
    if not user_rows:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
            }
        )
    
    user = user_rows[0]
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
            }
        )
    
    # Check if email is verified
    if not user["is_verified"]:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "EMAIL_NOT_VERIFIED",
                "message": "Please verify your email before logging in",
            }
        )
    
    # Create JWT token
    token = create_jwt_token(user["id"], user["organization_id"])
    
    # Create session record
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    session_id = q(
        """INSERT INTO session (user_id, token, expires_at, created_at)
           VALUES (%s, %s, %s, %s)""",
        (user["id"], token, expires_at, datetime.datetime.utcnow())
    )
    
    # Set HTTP-only cookie with secure attributes
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # Requires HTTPS in production
        samesite="strict",
        max_age=24 * 60 * 60,  # 24 hours in seconds
    )
    
    # Get organization name
    org_rows = q("SELECT name FROM organization WHERE id=%s", (user["organization_id"],))
    org_name = org_rows[0]["name"] if org_rows else None
    
    return {
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "organization_id": user["organization_id"],
            "organization_name": org_name,
        }
    }


@app.post("/api/auth/logout")
async def logout(
    response: Response, 
    current_user: Dict[str, Any] = Depends(get_current_user),
    access_token: Optional[str] = Cookie(None)
):
    """
    Logout user by invalidating session in database and clearing cookies.
    """
    # Invalidate session in database
    if access_token:
        from auth import invalidate_session
        invalidate_session(access_token)
    
    # Clear authentication cookie
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )
    
    return {"message": "Logged out successfully"}


@app.get("/api/auth/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    return {
        "user": current_user
    }


# ========== Domain Management Endpoints ==========

@app.post("/api/domains")
async def create_domain(
    domain_data: DomainCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Add a new domain for the user's organization.
    Generates a unique verification token.
    """
    domain = add_domain(current_user["id"], domain_data.domain_name)
    
    return {
        "message": "Domain added successfully. Please verify ownership.",
        "domain": {
            "id": domain["id"],
            "domain_name": domain["domain_name"],
            "verification_token": domain["verification_token"],
            "is_verified": domain["is_verified"],
            "created_at": domain["created_at"].isoformat() if domain["created_at"] else None,
        }
    }


@app.get("/api/domains")
async def list_domains(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all domains for the user's organization.
    """
    domains = get_user_domains(current_user["id"])
    
    return {
        "domains": [
            {
                "id": d["id"],
                "domain_name": d["domain_name"],
                "is_verified": d["is_verified"],
                "verification_method": d.get("verification_method"),
                "verified_at": d["verified_at"].isoformat() if d.get("verified_at") else None,
                "created_at": d["created_at"].isoformat() if d.get("created_at") else None,
            }
            for d in domains
        ]
    }


@app.get("/api/domains/{domain_id}")
async def get_domain_details(
    domain_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get domain details with verification instructions.
    """
    domain = get_domain_by_id(domain_id, current_user["id"])
    
    # Prepare verification instructions
    verification_instructions = {
        "meta_tag": {
            "method": "HTML Meta Tag",
            "description": "Add this meta tag to the <head> section of your homepage",
            "code": f'<meta name="accessify-verification" content="{domain["verification_token"]}">',
            "location": f"https://{domain['domain_name']}/index.html (in <head> section)",
        },
        "wellknown": {
            "method": "Well-Known File",
            "description": "Create a text file at this location with your verification token",
            "code": domain["verification_token"],
            "location": f"https://{domain['domain_name']}/.well-known/accessify-verification.txt",
        }
    }
    
    return {
        "domain": {
            "id": domain["id"],
            "domain_name": domain["domain_name"],
            "verification_token": domain["verification_token"],
            "is_verified": domain["is_verified"],
            "verification_method": domain.get("verification_method"),
            "verified_at": domain["verified_at"].isoformat() if domain.get("verified_at") else None,
            "created_at": domain["created_at"].isoformat() if domain.get("created_at") else None,
        },
        "verification_instructions": verification_instructions,
    }


@app.post("/api/domains/{domain_id}/verify")
async def verify_domain_endpoint(
    domain_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Trigger domain verification.
    Checks for verification token in meta tag or well-known file.
    """
    result = await verify_domain(domain_id, current_user["id"])
    
    if result["success"]:
        return {
            "message": result["message"],
            "verified": True,
            "method": result["method"],
            "verified_at": result["verified_at"],
        }
    else:
        return JSONResponse(
            status_code=400,
            content={
                "message": result["message"],
                "verified": False,
                "troubleshooting": result.get("troubleshooting", {}),
            }
        )


@app.delete("/api/domains/{domain_id}")
async def remove_domain(
    domain_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Remove a domain from the organization.
    """
    delete_domain(domain_id, current_user["id"])
    
    return {
        "message": "Domain removed successfully"
    }


# ========== Ethics Agreement Endpoints ==========

@app.get("/api/ethics/current")
async def get_current_ethics_agreement():
    """
    Get the current ethics agreement.
    Returns the full agreement text, version number, and effective date.
    """
    agreement = get_current_agreement()
    
    return {
        "agreement": {
            "version": agreement["version"],
            "content": agreement["content"],
            "effective_date": agreement["effective_date"].isoformat() if agreement.get("effective_date") else None,
        }
    }


@app.post("/api/ethics/accept")
async def accept_ethics_agreement(
    acceptance_data: EthicsAcceptance,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Accept the ethics agreement.
    Records the acceptance with user ID, agreement version, timestamp, and IP address.
    Creates an audit trail entry.
    """
    acceptance = record_acceptance(
        user_id=current_user["id"],
        version=acceptance_data.agreement_version,
        ip_address=acceptance_data.ip_address
    )
    
    return {
        "message": "Ethics agreement accepted successfully",
        "acceptance": {
            "id": acceptance["id"],
            "agreement_version": acceptance["agreement_version"],
            "accepted_at": acceptance["accepted_at"].isoformat() if acceptance.get("accepted_at") else None,
        }
    }


@app.get("/api/ethics/status")
async def get_ethics_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Check the user's ethics agreement acceptance status.
    Returns whether they have accepted the current version and need to accept.
    """
    status = get_acceptance_status(current_user["id"])
    
    # Also include acceptance history
    history = get_acceptance_history(current_user["id"])
    
    return {
        "status": status,
        "history": [
            {
                "id": h["id"],
                "agreement_version": h["agreement_version"],
                "accepted_at": h["accepted_at"].isoformat() if h.get("accepted_at") else None,
                "ip_address": h.get("ip_address"),
            }
            for h in history
        ]
    }


# ========== Website Management Endpoints ==========

@app.post("/api/websites")
async def create_website(
    website_data: WebsiteCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Register a new website for remediation.
    Requires ethics agreement acceptance.
    Validates that the URL domain matches a verified domain owned by the user.
    """
    # Check ethics agreement acceptance
    require_ethics_acceptance(current_user["id"])
    
    # Register the website
    website = register_website(
        user_id=current_user["id"],
        entry_url=website_data.entry_url,
        domain_id=website_data.domain_id,
        name=website_data.name
    )
    
    return {
        "message": "Website registered successfully",
        "website": {
            "id": website["id"],
            "entry_url": website["entry_url"],
            "domain_id": website["domain_id"],
            "name": website.get("name"),
            "status": website["status"],
            "created_at": website["created_at"].isoformat() if website.get("created_at") else None,
        }
    }


@app.get("/api/websites")
async def list_websites(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    List all websites registered by the user.
    Returns websites with domain information and remediation status.
    """
    websites = get_user_websites(current_user["id"])
    
    return {
        "websites": [
            {
                "id": w["id"],
                "entry_url": w["entry_url"],
                "name": w.get("name"),
                "domain_id": w["domain_id"],
                "domain_name": w.get("domain_name"),
                "domain_verified": w.get("domain_verified"),
                "status": w["status"],
                "last_remediation_at": w["last_remediation_at"].isoformat() if w.get("last_remediation_at") else None,
                "created_at": w["created_at"].isoformat() if w.get("created_at") else None,
            }
            for w in websites
        ]
    }


@app.get("/api/websites/{website_id}")
async def get_website(
    website_id: int,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Get detailed information about a specific website.
    Returns website details with domain information.
    Public access allowed for remediated websites.
    """
    
    # Get website with domain information
    website_rows = q(
        """SELECT 
               w.*,
               d.domain_name,
               d.is_verified as domain_verified
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
    
    # If website is remediated, allow public access
    # Otherwise, require authentication and ownership
    if website["status"] != "remediated":
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail="Authentication required"
            )
        if website["user_id"] != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this website"
            )
    
    return {
        "website": {
            "id": website["id"],
            "entry_url": website["entry_url"],
            "name": website.get("name"),
            "domain_id": website["domain_id"],
            "domain_name": website.get("domain_name"),
            "domain_verified": website.get("domain_verified"),
            "status": website["status"],
            "last_remediation_at": website["last_remediation_at"].isoformat() if website.get("last_remediation_at") else None,
            "created_at": website["created_at"].isoformat() if website.get("created_at") else None,
        }
    }


@app.delete("/api/websites/{website_id}")
async def remove_website(
    website_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Remove a website from the user's account.
    """
    delete_website(website_id, current_user["id"])
    
    return {
        "message": "Website removed successfully"
    }


@app.get("/api/websites/public/remediated")
async def list_public_remediated_websites():
    """
    Public endpoint to list all remediated websites.
    No authentication required - shows all successfully remediated websites.
    """
    # Get all remediated websites with domain information
    websites = q(
        """SELECT 
               w.id,
               w.entry_url,
               w.name,
               w.status,
               w.last_remediation_at,
               w.created_at,
               d.domain_name
           FROM website w
           JOIN domain d ON w.domain_id = d.id
           WHERE w.status = 'remediated'
           ORDER BY w.last_remediation_at DESC""",
        ()
    )
    
    return {
        "websites": [
            {
                "id": w["id"],
                "entry_url": w["entry_url"],
                "name": w.get("name"),
                "domain_name": w.get("domain_name"),
                "status": w["status"],
                "last_remediation_at": w["last_remediation_at"].isoformat() if w.get("last_remediation_at") else None,
                "created_at": w["created_at"].isoformat() if w.get("created_at") else None,
            }
            for w in (websites or [])
        ]
    }


# ========== Remediation Endpoints ==========

@app.post("/api/websites/{website_id}/remediate")
async def remediate_website(
    website_id: int,
    mode: str = Query("fast"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Start remediation for a registered website.
    Triggers the full pipeline: fetch, audit, fix, embed.
    """
    # Validate user owns the website
    website = get_website_details(website_id, current_user["id"])
    
    # Check ethics agreement acceptance
    require_ethics_acceptance(current_user["id"])
    
    # Update status to processing
    q("UPDATE website SET status=%s WHERE id=%s", ("processing", website_id))
    
    try:
        # Call the existing process endpoint logic
        url = website["entry_url"]
        
        # Fetch HTML
        try:
            html = await fetch_html(url)
        except Exception as e:
            q("UPDATE website SET status=%s WHERE id=%s", ("error", website_id))
            raise HTTPException(400, f"Failed to fetch: {e}")

        domain = urllib.parse.urlparse(url).netloc

        # Create page linked to website
        page_id = q(
            "INSERT INTO page (url, domain, raw_html, status, created_at, website_id) VALUES (%s,%s,%s,%s,%s,%s)",
            (url, domain, html, "NEW", datetime.datetime.utcnow(), website_id)
        )

        # Extract chunks & insert
        parts = extract_chunks(html)
        if parts:
            rows = []
            for c in parts:
                rows.append((
                    page_id,
                    (c.get("path") or "")[:1024],
                    c.get("role"),
                    c.get("text"),
                    json.dumps(c.get("attrs") or {}),
                    None
                ))
            q("""INSERT INTO chunk (page_id, path, role, text, attrs, embedding)
                 VALUES (%s,%s,%s,%s,%s,%s)""", rows, many=True)

        # Audit
        db_chunks = q("SELECT * FROM chunk WHERE page_id=%s", (page_id,))
        normalized_chunks = []
        for r in db_chunks:
            normalized_chunks.append({
                "id": r["id"],
                "role": r["role"],
                "path": r["path"],
                "text": r["text"] or "",
                "attrs": ensure_dict(r["attrs"])
            })
        issues = audit(normalized_chunks)
        if issues:
            ins = [(page_id, c.get("id"), itype, sev, json.dumps(details))
                   for (itype, sev, details, c) in issues]
            q("""INSERT INTO issue (page_id, chunk_id, type, severity, details)
                 VALUES (%s,%s,%s,%s,%s)""", ins, many=True)
        q("UPDATE page SET status='AUDITED' WHERE id=%s", (page_id,))

        # Fix & normalize URLs
        issues_db = q("SELECT * FROM issue WHERE page_id=%s", (page_id,))
        by_id = {c["id"]: c for c in db_chunks}
        fixes_input = []
        for it in issues_db:
            det = ensure_dict(it["details"])
            c = by_id.get(it["chunk_id"], {})
            chunk_obj = {
                "role": c.get("role"),
                "text": c.get("text"),
                "attrs": ensure_dict(c.get("attrs")),
            }
            fixes_input.append((it["type"], it["severity"], det, chunk_obj))

        fixed_html = apply_fixes(html, fixes_input, page_url=url)
        q("UPDATE page SET fixed_html=%s, status='FIXED' WHERE id=%s", (fixed_html, page_id))

        # Embed chunks for RAG
        topk = 24 if (mode or "fast").lower() == "fast" else 64
        if openai_client:
            to_embed = select_chunks_for_embedding(db_chunks, k=topk)
            texts = [r["text"] for r in to_embed]
            vecs = embed_texts_batched(texts)

            updates = []
            for r, vec in zip(to_embed, vecs):
                vec_lit = json.dumps(vec) if vec else None
                updates.append((vec_lit, r["id"]))
            if updates:
                q("UPDATE chunk SET embedding=%s WHERE id=%s", updates, many=True)

        # Update website status
        q(
            "UPDATE website SET status=%s, last_remediation_at=%s WHERE id=%s",
            ("remediated", datetime.datetime.utcnow(), website_id)
        )
        
        # Generate preview URL and iframe snippet
        preview_url = generate_preview_url(page_id)
        iframe_snippet = generate_iframe_snippet(preview_url, website["domain_name"])

        return {
            "message": "Remediation completed successfully",
            "page_id": page_id,
            "preview_url": preview_url,
            "iframe_snippet": iframe_snippet,
            "issues_found": len(issues),
            "issues_fixed": len(issues),
            "status": "remediated"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Update status to error
        q("UPDATE website SET status=%s WHERE id=%s", ("error", website_id))
        raise HTTPException(500, f"Remediation failed: {str(e)}")


@app.get("/api/websites/{website_id}/status")
async def get_remediation_status(
    website_id: int,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Get the current remediation status for a website.
    Returns status, last remediation time, and issue counts if available.
    Public access allowed for remediated websites.
    """
    
    # Get website
    website_rows = q("SELECT * FROM website WHERE id=%s", (website_id,))
    if not website_rows:
        raise HTTPException(status_code=404, detail="Website not found")
    
    website = website_rows[0]
    
    # If website is not remediated, require authentication and ownership
    if website["status"] != "remediated":
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        if website["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="You don't have access to this website")
    
    # Get the most recent page for this website
    page_rows = q(
        """SELECT id, status, created_at 
           FROM page 
           WHERE website_id=%s 
           ORDER BY created_at DESC 
           LIMIT 1""",
        (website_id,)
    )
    
    page_info = None
    issue_count = 0
    
    if page_rows:
        page = page_rows[0]
        page_info = {
            "page_id": page["id"],
            "page_status": page["status"],
            "created_at": page["created_at"].isoformat() if page.get("created_at") else None,
        }
        
        # Get issue count
        issue_rows = q(
            "SELECT COUNT(*) as count FROM issue WHERE page_id=%s",
            (page["id"],)
        )
        if issue_rows:
            issue_count = issue_rows[0]["count"]
    
    return {
        "website_id": website_id,
        "status": website["status"],
        "last_remediation_at": website["last_remediation_at"].isoformat() if website.get("last_remediation_at") else None,
        "page": page_info,
        "issues_found": issue_count,
    }


@app.get("/api/websites/{website_id}/preview")
async def get_preview_info(
    website_id: int,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Get preview URL and iframe snippet for a remediated website.
    Returns 404 if website hasn't been remediated yet.
    Public access allowed for remediated websites.
    """
    
    # Get website with domain information
    website_rows = q(
        """SELECT w.*, d.domain_name 
           FROM website w
           JOIN domain d ON w.domain_id = d.id
           WHERE w.id=%s""",
        (website_id,)
    )
    if not website_rows:
        raise HTTPException(status_code=404, detail="Website not found")
    
    website = website_rows[0]
    
    # Check if website has been remediated
    if website["status"] != "remediated":
        # If not remediated, require authentication and ownership
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        if website["user_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="You don't have access to this website")
        
        raise HTTPException(
            status_code=400,
            detail={
                "code": "NOT_REMEDIATED",
                "message": "Website has not been remediated yet",
                "current_status": website["status"],
            }
        )
    
    # Get the most recent page for this website
    page_rows = q(
        """SELECT id, fixed_html, created_at 
           FROM page 
           WHERE website_id=%s AND status='FIXED'
           ORDER BY created_at DESC 
           LIMIT 1""",
        (website_id,)
    )
    
    if not page_rows:
        raise HTTPException(
            status_code=404,
            detail="No remediated content found for this website"
        )
    
    page = page_rows[0]
    
    # Generate preview URL and iframe snippet
    preview_url = generate_preview_url(page["id"])
    iframe_snippet = generate_iframe_snippet(preview_url, website["domain_name"])
    
    # Get issue statistics
    issue_rows = q(
        """SELECT COUNT(*) as total_issues,
           SUM(CASE WHEN severity='critical' THEN 1 ELSE 0 END) as critical_issues,
           SUM(CASE WHEN severity='serious' THEN 1 ELSE 0 END) as serious_issues
           FROM issue WHERE page_id=%s""",
        (page["id"],)
    )
    
    issue_stats = {
        "total_issues": 0,
        "critical_issues": 0,
        "serious_issues": 0,
    }
    
    if issue_rows:
        issue_stats = {
            "total_issues": issue_rows[0]["total_issues"] or 0,
            "critical_issues": issue_rows[0]["critical_issues"] or 0,
            "serious_issues": issue_rows[0]["serious_issues"] or 0,
        }
    
    return {
        "page_id": page["id"],
        "preview_url": preview_url,
        "iframe_snippet": iframe_snippet,
        "remediated_at": page["created_at"].isoformat() if page.get("created_at") else None,
        "issue_stats": issue_stats,
    }


# ========== Existing Routes ==========

@app.get("/health")
def health():
    q("SELECT 1")
    return {"ok": True}

@app.get("/output/{page_id}", response_class=HTMLResponse)
def output_html(page_id: int, response: Response):
    """
    Serve remediated HTML with CORS headers for verified domain.
    This endpoint is public (no auth required) to allow embedding.
    Injects accessibility toolbar for enhanced user experience.
    """
    # Get the page and associated website/domain
    page_rows = q(
        """SELECT p.fixed_html, w.domain_id, d.domain_name, d.is_verified
           FROM page p
           LEFT JOIN website w ON p.website_id = w.id
           LEFT JOIN domain d ON w.domain_id = d.id
           WHERE p.id=%s""",
        (page_id,)
    )
    
    if not page_rows or not page_rows[0]["fixed_html"]:
        raise HTTPException(404, "No fixed HTML yet.")
    
    page = page_rows[0]
    fixed_html = page["fixed_html"]
    
    # Inject accessibility toolbar script before closing body tag
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    toolbar_script = f"""
    <link rel="stylesheet" href="{base_url}/static/accessibility-toolbar.css">
    <script>
        window.ACCESSIFY_PAGE_ID = {page_id};
        window.ACCESSIFY_API_BASE = '{base_url}';
    </script>
    <script src="{base_url}/static/accessibility-toolbar.js"></script>
    """
    
    # Inject before closing body tag, or at the end if no body tag
    if "</body>" in fixed_html.lower():
        fixed_html = fixed_html.replace("</body>", f"{toolbar_script}</body>", 1)
    else:
        fixed_html += toolbar_script
    
    # Set proper content-type header
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    
    # Add CORS headers if domain is verified
    if page.get("is_verified") and page.get("domain_name"):
        domain_name = page["domain_name"]
        # Allow embedding from the verified domain (with and without www)
        response.headers["Access-Control-Allow-Origin"] = f"https://{domain_name}"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        # Also set X-Frame-Options to allow framing from the verified domain
        response.headers["X-Frame-Options"] = f"ALLOW-FROM https://{domain_name}"
        # Set Content-Security-Policy to allow framing from verified domain
        response.headers["Content-Security-Policy"] = f"frame-ancestors 'self' https://{domain_name} https://www.{domain_name}"
    
    return HTMLResponse(content=fixed_html, status_code=200)

@app.post("/process")
async def process(
    website_id: int = Query(...),
    mode: str = Query("fast"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    One-click pipeline:
    1) Validate user owns the website
    2) fetch HTML from website entry URL
    3) save page+chunks linked to website
    4) audit, 5) fix & normalize for standalone viewing,
    6) embed chunks for RAG, 7) return page_id + short summary.
    """
    # 1) Validate user owns the website
    website = get_website_details(website_id, current_user["id"])
    url = website["entry_url"]
    
    # 2) fetch HTML
    try:
        html = await fetch_html(url)
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch: {e}")

    domain = urllib.parse.urlparse(url).netloc

    # 3) create page linked to website
    page_id = q(
        "INSERT INTO page (url, domain, raw_html, status, created_at, website_id) VALUES (%s,%s,%s,%s,%s,%s)",
        (url, domain, html, "NEW", datetime.datetime.utcnow(), website_id)
    )

    # 3) extract chunks & insert (attrs as JSON text)
    parts = extract_chunks(html)  # -> list of {role, path, text, attrs}
    if parts:
        rows = []
        for c in parts:
            rows.append((
                page_id,
                (c.get("path") or "")[:1024],
                c.get("role"),
                c.get("text"),
                json.dumps(c.get("attrs") or {}),
                None  # embedding to be filled later
            ))
        q("""INSERT INTO chunk (page_id, path, role, text, attrs, embedding)
             VALUES (%s,%s,%s,%s,%s,%s)""", rows, many=True)

    # 4) audit
    db_chunks = q("SELECT * FROM chunk WHERE page_id=%s", (page_id,))
    normalized_chunks = []
    for r in db_chunks:
        normalized_chunks.append({
            "id": r["id"],
            "role": r["role"],
            "path": r["path"],
            "text": r["text"] or "",
            "attrs": ensure_dict(r["attrs"])
        })
    issues = audit(normalized_chunks)
    if issues:
        ins = [(page_id, c.get("id"), itype, sev, json.dumps(details))
               for (itype, sev, details, c) in issues]
        q("""INSERT INTO issue (page_id, chunk_id, type, severity, details)
             VALUES (%s,%s,%s,%s,%s)""", ins, many=True)
    q("UPDATE page SET status='AUDITED' WHERE id=%s", (page_id,))

    # 5) fix & normalize URLs for standalone viewing
    issues_db = q("SELECT * FROM issue WHERE page_id=%s", (page_id,))
    by_id = {c["id"]: c for c in db_chunks}
    fixes_input = []
    for it in issues_db:
        det = ensure_dict(it["details"])
        c = by_id.get(it["chunk_id"], {})
        chunk_obj = {
            "role": c.get("role"),
            "text": c.get("text"),
            "attrs": ensure_dict(c.get("attrs")),
        }
        fixes_input.append((it["type"], it["severity"], det, chunk_obj))

    fixed_html = apply_fixes(html, fixes_input, page_url=url)
    q("UPDATE page SET fixed_html=%s, status='FIXED' WHERE id=%s", (fixed_html, page_id))

    topk = 64 if mode != "fast" else 24
    # 6) embed chunks for RAG (batched & limited for speed)
    if openai_client:
        topk = 24 if (mode or "fast").lower() == "fast" else 64
        to_embed = select_chunks_for_embedding(db_chunks, k=topk)
        texts = [r["text"] for r in to_embed]
        vecs = embed_texts_batched(texts)

    updates = []
    for r, vec in zip(to_embed, vecs):
        vec_lit = json.dumps(vec) if vec else None  # TiDB accepts '[...]' for VECTOR
        updates.append((vec_lit, r["id"]))
    if updates:
        q("UPDATE chunk SET embedding=%s WHERE id=%s", updates, many=True)


    # 7) brief summary
    page_text = "\n\n".join([r["text"] or "" for r in db_chunks])[:10000]
    summary = llm_summary_from_text(page_text) if openai_client else ""
    
    # 8) Update website status and last_remediation_at
    q(
        "UPDATE website SET status=%s, last_remediation_at=%s WHERE id=%s",
        ("remediated", datetime.datetime.utcnow(), website_id)
    )

    return {"page_id": page_id, "summary": summary, "issues": len(issues)}

@app.post("/chat/{page_id}")
def chat_page(
    page_id: int,
    body: dict = Body(...),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Retrieval-augmented Q/A over this page:
    - Public access allowed for remediated websites
    - embed the question
    - KNN over chunk.embedding (cosine)
    - answer grounded in top chunks
    - references accessibility fixes applied
    """
    question = (body.get("question") or "").strip()
    if not question:
        raise HTTPException(400, "Missing question")

    if not openai_client:
        return {"answer": "Chat is disabled (no API key configured)."}

    # Get page and website information
    page_rows = q(
        """SELECT p.id, p.website_id, w.user_id, w.status as website_status
           FROM page p
           LEFT JOIN website w ON p.website_id = w.id
           WHERE p.id = %s""",
        (page_id,)
    )
    
    if not page_rows:
        raise HTTPException(404, "Page not found")
    
    page = page_rows[0]
    
    # Check if page is associated with a website
    if page["website_id"] is not None:
        # If website is not remediated, require authentication and ownership
        if page["website_status"] != "remediated":
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            if page["user_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "code": "UNAUTHORIZED",
                        "message": "You do not have permission to access this page"
                    }
                )
        # If website is remediated, allow public access (no authentication check needed)

    # a) embed query
    qvec = openai_client.embeddings.create(model=EMBED_MODEL, input=question).data[0].embedding
    qvec_lit = json.dumps(qvec)  # pass as JSON string literal for TiDB VECTOR

    # b) retrieve top-k chunks for this page
    # Try vector search first (TiDB), fallback to simple retrieval (MySQL)
    try:
        hits = q("""
            SELECT text, VEC_COSINE_DISTANCE(embedding, %s) AS distance
            FROM chunk
            WHERE page_id = %s
            ORDER BY distance
            LIMIT 8
        """, (qvec_lit, page_id))
    except Exception as e:
        # Fallback for local MySQL without vector functions
        if "VEC_COSINE_DISTANCE" in str(e) or "FUNCTION" in str(e):
            hits = q("""
                SELECT text
                FROM chunk
                WHERE page_id = %s AND embedding IS NOT NULL
                ORDER BY id
                LIMIT 8
            """, (page_id,))
        else:
            raise

    context = "\n\n".join([h["text"] or "" for h in hits])[:8000]
    if not context.strip():
        return {"answer": "I couldn't find content to answer that on this page."}

    # c) Get accessibility fixes applied to this page
    fixes_rows = q(
        """SELECT type, severity, details
           FROM issue
           WHERE page_id = %s
           ORDER BY severity DESC""",
        (page_id,)
    )
    
    fixes_summary = ""
    if fixes_rows:
        # Group fixes by type
        fix_types = {}
        for fix in fixes_rows:
            fix_type = fix["type"]
            if fix_type not in fix_types:
                fix_types[fix_type] = 0
            fix_types[fix_type] += 1
        
        # Create a summary of fixes
        fix_list = [f"{count} {fix_type} issue(s)" for fix_type, count in fix_types.items()]
        fixes_summary = f"\n\nAccessibility improvements applied to this page: {', '.join(fix_list)}."

    # d) answer with LLM, including fix information
    prompt = (
        "Answer the user's question using only the provided page content.\n"
        "If the user asks about accessibility improvements or fixes, reference the specific improvements listed below.\n\n"
        f"CONTENT:\n{context}\n"
        f"{fixes_summary}\n"
        f"QUESTION: {question}\n\nANSWER:"
    )
    r = openai_client.responses.create(
        model=CHAT_MODEL,
        input=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_output_tokens=400,
    )
    return {"answer": (r.output_text or '').strip()}

