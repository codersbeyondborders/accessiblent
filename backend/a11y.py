# a11y.py
from __future__ import annotations

from bs4 import BeautifulSoup, NavigableString, Tag
from typing import Dict, List, Tuple, Any

# ----------------------------------
# Chunk extraction
# ----------------------------------

def _nth_of_type(el: Tag) -> int:
    """1-based index of element among siblings of the same tag name."""
    if not el or not el.name or not el.parent:
        return 1
    n = 0
    for sib in el.parent.find_all(el.name, recursive=False):
        n += 1
        if sib is el:
            return n
    return 1

def _css_path(el: Tag) -> str:
    """Create a short, stable CSS-like path e.g. html>body>div:nth-of-type(2)>h2."""
    parts = []
    cur = el
    hops = 0
    while isinstance(cur, Tag) and cur.name and hops < 12:
        idx = _nth_of_type(cur)
        seg = cur.name
        # only add :nth-of-type when needed (if not first of kind)
        if cur.parent and len(cur.parent.find_all(cur.name, recursive=False)) > 1:
            seg += f":nth-of-type({idx})"
        parts.append(seg)
        cur = cur.parent
        hops += 1
    parts.reverse()
    return ">".join(parts) or (el.name or "node")

def _text_of(el: Tag) -> str:
    """Normalized visible text for a tag (no script/style)."""
    if not isinstance(el, Tag):
        return ""
    for bad in el.find_all(["script", "style", "noscript"]):
        bad.extract()
    return el.get_text(" ", strip=True)

def _is_visible_text_block(el: Tag) -> bool:
    """Heuristic: consider paragraphs/list-items/sections as content blocks."""
    if not isinstance(el, Tag):
        return False
    tag = (el.name or "").lower()
    if tag in {"p", "li", "article", "section"}:
        return True
    if tag in {"div"}:
        # treat divs with plenty of text and few children as blocks
        t = _text_of(el)
        return len(t) >= 120
    return False

def extract_chunks(html: str) -> List[Dict[str, Any]]:
    """
    Produce a list of chunks:
      - role: 'img' | 'heading' | 'link' | 'section'
      - path: CSS-like path for stable targeting
      - text: normalized inner text ('' for images)
      - attrs: dict of relevant attributes
    """
    soup = BeautifulSoup(html or "", "lxml")
    chunks: List[Dict[str, Any]] = []

    # Images
    for img in soup.find_all("img"):
        attrs = {
            "src": (img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-lazy") or "").strip(),
            "alt": (img.get("alt") or "").strip(),
            "width": (img.get("width") or "").strip(),
            "height": (img.get("height") or "").strip(),
        }
        chunks.append({
            "role": "img",
            "path": _css_path(img),
            "text": "",
            "attrs": attrs,
        })

    # Headings (h1..h6)
    for level in range(1, 7):
        for h in soup.find_all(f"h{level}"):
            text = _text_of(h)
            attrs = {"tag": f"h{level}"}
            chunks.append({
                "role": "heading",
                "path": _css_path(h),
                "text": text,
                "attrs": attrs,
            })

    # Links
    for a in soup.find_all("a"):
        text = _text_of(a)
        # compress whitespace to compare later in audit
        attrs = {
            "href": (a.get("href") or "").strip(),
            "aria-label": (a.get("aria-label") or "").strip(),
            "title": (a.get("title") or "").strip(),
        }
        chunks.append({
            "role": "link",
            "path": _css_path(a),
            "text": text,
            "attrs": attrs,
        })

    # Sections / content blocks (for RAG context)
    # Only include blocks with reasonable text length to keep the DB lean.
    for el in soup.find_all(True):
        if _is_visible_text_block(el):
            text = _text_of(el)
            if len(text) >= 60:
                chunks.append({
                    "role": "section",
                    "path": _css_path(el),
                    "text": text,
                    "attrs": {"tag": el.name},
                })

    return chunks


# ----------------------------------
# Audit rules
# ----------------------------------

_VAGUE_LINK_TEXT = {
    "click here", "read more", "learn more", "more", "here",
    "details", "link", "this", "go", "open", "continue"
}

def _as_dict(val: Any) -> dict:
    if isinstance(val, dict): 
        return val
    if not val: 
        return {}
    if isinstance(val, str):
        try:
            import json
            return json.loads(val)
        except Exception:
            return {}
    return {}

def audit(chunks: List[Dict[str, Any]]) -> List[Tuple[str, str, Dict[str, Any], Dict[str, Any]]]:
    """
    Inspect extracted chunks and emit issues as tuples:
      (issue_type, severity, details, chunk)

    Issues:
      - MISSING_ALT (MEDIUM): <img> with missing/empty alt
      - BAD_HEADING_ORDER (LOW): heading level jumps by > 1
      - POOR_LINK_TEXT (LOW): vague/ambiguous link text
    """
    issues: List[Tuple[str, str, Dict[str, Any], Dict[str, Any]]] = []

    # ---- Images: missing/empty alt
    for c in chunks:
        if c.get("role") == "img":
            attrs = _as_dict(c.get("attrs"))
            alt = (attrs.get("alt") or "").strip()
            if not alt:
                issues.append((
                    "MISSING_ALT",
                    "MEDIUM",
                    {"reason": "Image without alt attribute or empty alt"},
                    c
                ))

    # ---- Headings: detect level jumps
    last_level = 0
    for c in [x for x in chunks if x.get("role") == "heading"]:
        attrs = _as_dict(c.get("attrs"))
        tag = (attrs.get("tag") or "").strip().lower()
        level = 0
        if len(tag) == 2 and tag.startswith("h") and tag[1].isdigit():
            level = int(tag[1])
        if last_level and level and (level - last_level) > 1:
            issues.append((
                "BAD_HEADING_ORDER",
                "LOW",
                {"prev": last_level, "curr": level},
                c
            ))
        if level:
            last_level = level

    # ---- Links: vague text
    for c in [x for x in chunks if x.get("role") == "link"]:
        text = (c.get("text") or "").strip().lower()
        if text in _VAGUE_LINK_TEXT:
            issues.append((
                "POOR_LINK_TEXT",
                "LOW",
                {"text": c.get("text")},
                c
            ))

    return issues
