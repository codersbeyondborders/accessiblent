# fixer.py
import os
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# ---------- OpenAI (lazy) ----------
def _get_openai():
    """
    Returns (client, model) or None if OPENAI_API_KEY is missing or SDK unavailable.
    """
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=key)
        model = os.getenv("CHAT_MODEL", "gpt-4o-mini")
        return client, model
    except Exception:
        return None

def generate_alt(context_text: str) -> str:
    """
    Generates short, objective alt text (<= 12 words) using OpenAI if available.
    Falls back to 'Image' on any error or if no API key is set.
    """
    cm = _get_openai()
    if not cm:
        return "Image"
    client, model = cm
    prompt = (
        "Write a short, objective alt text (max 12 words) for this image context. "
        "Avoid opinions, punctuation beyond commas/periods, and avoid quoting.\n\n"
        f"Context:\n{(context_text or '')[:500]}\n\nAlt:"
    )
    try:
        resp = client.responses.create(
            model=model,
            input=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_output_tokens=40,
        )
        text = (getattr(resp, "output_text", "") or "").strip().strip('"').strip()
        return text or "Image"
    except Exception:
        return "Image"

# ---------- Utilities ----------
def _as_dict(val):
    """Best-effort convert val into a dict (supports JSON strings, None)."""
    if isinstance(val, dict):
        return val
    if not val:
        return {}
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return {}
    return {}

def _abs_url(base_url: str, val: str) -> str:
    """Make a URL absolute relative to base_url (handles //, /, and relative)."""
    try:
        return urljoin(base_url, val)
    except Exception:
        return val

def _fix_srcset(base_url: str, srcset: str) -> str:
    """
    Normalize a srcset string:
    "url1 1x, url2 2x" or "url 480w, url 800w" → make each url absolute.
    """
    parts = []
    for item in (srcset or "").split(","):
        item = item.strip()
        if not item:
            continue
        segs = item.split()
        if not segs:
            continue
        segs[0] = _abs_url(base_url, segs[0])
        parts.append(" ".join(segs))
    return ", ".join(parts)

def normalize_urls(soup: BeautifulSoup, page_url: str):
    """
    Ensure the remediated HTML renders correctly when served from our domain:
    - Inject <base href="...">
    - Normalize <img src/srcset> (and common lazy-load attrs)
    - Normalize <a href>
    """
    try:
        head = soup.find("head")
        if head and not head.find("base"):
            base = soup.new_tag("base", href=page_url)
            head.insert(0, base)
    except Exception:
        pass

    # Images (src, data-src, srcset)
    for img in soup.find_all("img"):
        src = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-original")
            or img.get("data-lazy")
        )
        if src:
            img["src"] = _abs_url(page_url, src)
        if img.has_attr("srcset"):
            img["srcset"] = _fix_srcset(page_url, img.get("srcset") or "")

    # Links
    for a in soup.find_all("a"):
        href = a.get("href")
        if href and not href.startswith("javascript:"):
            a["href"] = _abs_url(page_url, href)

# ---------- Fix application ----------
def apply_fixes(raw_html: str, issues, page_url: str = ""):
    """
    Apply deterministic & LLM-based fixes to the HTML given a list of issues, then normalize URLs.
    issues: iterable of (issue_type, severity, details, chunk_dict)
            chunk_dict: { role, text, attrs } (attrs may be str or dict)
    """
    soup = BeautifulSoup(raw_html or "", "lxml")

    for (itype, _sev, _details, chunk) in issues:
        attrs = _as_dict((chunk or {}).get("attrs"))
        role = (chunk or {}).get("role")
        text = ((chunk or {}).get("text") or "").strip()

        # 1) Missing/empty alt on images → generate concise alt
        if itype == "MISSING_ALT" and role == "img":
            target_src = (attrs.get("src") or "").strip()
            candidates = []
            for img in soup.find_all("img"):
                if target_src:
                    if img.get("src") == target_src:
                        candidates = [img]
                        break
                else:
                    if not (img.get("alt") or "").strip():
                        candidates.append(img)
            for img in candidates or []:
                ctx = img.parent.get_text(" ", strip=True) if img.parent else ""
                alt = generate_alt(ctx)
                img["alt"] = alt or "Image"

        # 2) Heading level jumps → promote one level (e.g., h3->h2) for the matching heading
        elif itype == "BAD_HEADING_ORDER" and role == "heading":
            tag = (attrs.get("tag") or "").lower()
            try:
                level = int(tag[1]) if len(tag) > 1 and tag[1].isdigit() else 0
            except Exception:
                level = 0
            if level > 2 and tag in {"h3", "h4", "h5", "h6"}:
                new_tag = f"h{level - 1}"
                for h in soup.find_all(tag):
                    if h.get_text(strip=True) == text:
                        h.name = new_tag
                        break

        # 3) Vague link text → prefer aria-label, else derive from href
        elif itype == "POOR_LINK_TEXT" and role == "link":
            for a in soup.find_all("a"):
                if a.get_text(strip=True) == text:
                    label = a.get("aria-label")
                    if label:
                        a.string = label
                    else:
                        href = (a.get("href") or "").strip()
                        slug = (href.split("/")[-1] if "/" in href else href) or "learn-more"
                        slug = slug.split("?")[0].split("#")[0]
                        pretty = slug.replace("-", " ").replace("_", " ").strip().title() or "Learn More"
                        a.string = pretty
                    break

        # 4) Missing language attribute on <html>
        elif itype == "MISSING_LANG":
            html_tag = soup.find("html")
            if html_tag and not html_tag.get("lang"):
                # Default to English, could be enhanced with language detection
                html_tag["lang"] = "en"

        # 5) Missing main landmark
        elif itype == "MISSING_MAIN_LANDMARK":
            # Find the body tag
            body = soup.find("body")
            if body:
                # Check if <main> already exists
                if not soup.find("main"):
                    # Strategy: wrap the primary content in <main>
                    # Look for common content containers
                    main_candidates = (
                        body.find("div", class_=lambda x: x and any(
                            term in str(x).lower() for term in ["content", "main", "primary", "container"]
                        )) or
                        body.find("div", id=lambda x: x and any(
                            term in str(x).lower() for term in ["content", "main", "primary"]
                        ))
                    )
                    
                    if main_candidates:
                        # Wrap the candidate in <main>
                        main_tag = soup.new_tag("main")
                        main_candidates.wrap(main_tag)
                    else:
                        # Fallback: wrap all direct children of body (except header/footer/nav) in <main>
                        main_tag = soup.new_tag("main")
                        skip_tags = {"header", "footer", "nav", "script", "style"}
                        content_elements = []
                        
                        for child in list(body.children):
                            # Only process Tag elements (not NavigableString)
                            if hasattr(child, "name") and child.name and child.name not in skip_tags:
                                # Check if it's not already a landmark
                                role = child.get("role") if hasattr(child, "get") else None
                                if child.name not in {"main", "aside"} and role not in {"banner", "contentinfo", "navigation", "complementary"}:
                                    content_elements.append(child)
                        
                        if content_elements:
                            # Insert main before the first content element
                            first_elem = content_elements[0]
                            first_elem.insert_before(main_tag)
                            # Move all content elements into main
                            for elem in content_elements:
                                main_tag.append(elem.extract())

        # 6) Link without accessible name
        elif itype == "LINK_NO_NAME" and role == "link":
            href = attrs.get("href", "")
            for a in soup.find_all("a", href=href):
                # Check if link has no text content and no aria-label
                link_text = a.get_text(strip=True)
                aria_label = a.get("aria-label", "").strip()
                
                if not link_text and not aria_label:
                    # Generate accessible name from href
                    if href:
                        # Try to create meaningful label from URL
                        if "facebook" in href.lower():
                            a["aria-label"] = "Visit our Facebook page"
                        elif "twitter" in href.lower() or "x.com" in href.lower():
                            a["aria-label"] = "Visit our Twitter page"
                        elif "linkedin" in href.lower():
                            a["aria-label"] = "Visit our LinkedIn page"
                        elif "instagram" in href.lower():
                            a["aria-label"] = "Visit our Instagram page"
                        elif "youtube" in href.lower():
                            a["aria-label"] = "Visit our YouTube channel"
                        elif "github" in href.lower():
                            a["aria-label"] = "Visit our GitHub repository"
                        else:
                            # Generic fallback based on URL structure
                            domain = href.split("//")[-1].split("/")[0].replace("www.", "")
                            a["aria-label"] = f"Visit {domain}"
                    else:
                        # No href, use generic label
                        a["aria-label"] = "Link"
                    break

    # Normalize resource URLs & add <base>
    if page_url:
        normalize_urls(soup, page_url)

    return str(soup)
