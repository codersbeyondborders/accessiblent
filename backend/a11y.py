# a11y.py
from __future__ import annotations

from bs4 import BeautifulSoup, NavigableString, Tag
from typing import Dict, List, Tuple, Any
import re
import json

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
    if isinstance(val, dict): return val
    if not val: return {}
    if isinstance(val, str):
        try: return json.loads(val)
        except Exception: return {}
    return {}

# ---------- chunk extraction (add a few attrs we need to audit/fix) ----------
def extract_chunks(html: str) -> List[Dict[str, Any]]:
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
        chunks.append({"role":"img","path":_css_path(img),"text":"","attrs":attrs})

    # Headings
    for level in range(1,7):
        for h in soup.find_all(f"h{level}"):
            chunks.append({"role":"heading","path":_css_path(h),"text":_text_of(h),"attrs":{"tag":f"h{level}"}})

    # Links
    for a in soup.find_all("a"):
        attrs = {
            "href": (a.get("href") or "").strip(),
            "aria-label": (a.get("aria-label") or "").strip(),
            "title": (a.get("title") or "").strip(),
            "target": (a.get("target") or "").strip(),
            "rel": (a.get("rel") or []),
        }
        chunks.append({"role":"link","path":_css_path(a),"text":_text_of(a),"attrs":attrs})

    # Controls (inputs/selects/textarea/buttons)
    for ctrl in soup.find_all(["input","select","textarea","button"]):
        attrs = {
            "id": (ctrl.get("id") or "").strip(),
            "name": (ctrl.get("name") or "").strip(),
            "type": (ctrl.get("type") or "").strip().lower(),
            "aria-label": (ctrl.get("aria-label") or "").strip(),
            "aria-labelledby": (ctrl.get("aria-labelledby") or "").strip(),
            "placeholder": (ctrl.get("placeholder") or "").strip(),
            "tag": ctrl.name,
        }
        chunks.append({"role":"control","path":_css_path(ctrl),"text":_text_of(ctrl),"attrs":attrs})

    # Iframes
    for fr in soup.find_all("iframe"):
        chunks.append({"role":"iframe","path":_css_path(fr),"text":"","attrs":{"title":(fr.get("title") or "").strip()}})

    # SVGs
    for svg in soup.find_all("svg"):
        chunks.append({"role":"svg","path":_css_path(svg),"text":_text_of(svg),"attrs":{}})

    # Sections for RAG
    for el in soup.find_all(True):
        if _is_visible_text_block(el):
            text = _text_of(el)
            if len(text) >= 60:
                chunks.append({"role":"section","path":_css_path(el),"text":text,"attrs":{"tag":el.name}})

    # Document-level checks (add one synthetic chunk)
    head = soup.find("head")
    html_el = soup.find("html")
    chunks.append({
        "role":"document",
        "path":"html>head",
        "text":"",
        "attrs":{
            "has_title": bool(head and head.find("title")),
            "has_viewport": bool(head and head.find("meta", attrs={"name":"viewport"})),
            "has_charset": bool(head and head.find("meta", attrs={"charset":True})),
            "html_lang": (html_el.get("lang").strip() if html_el and html_el.get("lang") else ""),
            "has_skiplink": bool(soup.find("a", attrs={"href":"#main"}) or soup.find("a", string=re.compile(r"skip", re.I))),
            "has_main": bool(soup.find("main")),
            "has_nav": bool(soup.find("nav")),
        }
    })

    return chunks

# ---------- audit ----------
def audit(chunks: List[Dict[str, Any]]) -> List[Tuple[str,str,Dict[str,Any],Dict[str,Any]]]:
    issues: List[Tuple[str,str,Dict[str,Any],Dict[str,Any]]] = []

    # Images: missing/empty alt
    for c in chunks:
        if c["role"] == "img":
            alt = (_as_dict(c["attrs"]).get("alt") or "").strip()
            if not alt:
                issues.append(("MISSING_ALT","MEDIUM",{"reason":"Image missing alt"},c))

    # Headings: level jumps
    last = 0
    for c in [x for x in chunks if x["role"]=="heading"]:
        tag = (_as_dict(c["attrs"]).get("tag") or "").lower()
        lvl = int(tag[1]) if len(tag)==2 and tag[1].isdigit() else 0
        if last and lvl and (lvl-last)>1:
            issues.append(("BAD_HEADING_ORDER","LOW",{"prev":last,"curr":lvl},c))
        if lvl: last = lvl

    # Links: vague text
    for c in [x for x in chunks if x["role"]=="link"]:
        txt = (c.get("text") or "").strip().lower()
        if txt in _VAGUE_LINK_TEXT:
            issues.append(("POOR_LINK_TEXT","LOW",{"text":c.get("text")},c))

    # Links: no accessible name (no text, no aria-label, no title)
    for c in [x for x in chunks if x["role"]=="link"]:
        a = _as_dict(c["attrs"])
        name = (c.get("text") or "").strip() or a.get("aria-label","").strip() or a.get("title","").strip()
        if not name:
            issues.append(("LINK_NO_NAME","MEDIUM",{},c))

    # target=_blank without rel
    for c in [x for x in chunks if x["role"]=="link"]:
        a = _as_dict(c["attrs"])
        if (a.get("target") == "_blank"):
            rel = a.get("rel") or []
            if isinstance(rel,str): rel = [rel]
            rel_l = [r.lower() for r in rel]
            if "noopener" not in rel_l or "noreferrer" not in rel_l:
                issues.append(("BLANK_TARGET_NO_REL","LOW",{},c))

    # Controls: missing programmatic label
    # (has <label for=id> or aria-label/aria-labelledby or button text)
    for c in [x for x in chunks if x["role"]=="control"]:
        a = _as_dict(c["attrs"])
        if a.get("tag")=="button":
            if not (c.get("text") or "").strip():
                issues.append(("CONTROL_NO_LABEL","MEDIUM",{"tag":"button"},c))
        else:
            if not (a.get("aria-label") or a.get("aria-labelledby") or a.get("id")):
                issues.append(("CONTROL_NO_LABEL","MEDIUM",{"tag":a.get("tag")},c))

    # Iframe: missing title
    for c in [x for x in chunks if x["role"]=="iframe"]:
        t = (_as_dict(c["attrs"]).get("title") or "").strip()
        if not t:
            issues.append(("IFRAME_NO_TITLE","LOW",{},c))

    # SVG: no name (no title child, no aria-label)
    # (We only flag; fix will add aria-hidden for decorative or aria-label heuristic)
    for c in [x for x in chunks if x["role"]=="svg"]:
        if not (c.get("text") or "").strip():
            issues.append(("SVG_NO_NAME","LOW",{},c))

    # tabindex > 0
    # Detect via simple text search at fix time; here we only flag by role guess.
    # (Optional) Flag anchors acting as buttons
    for c in [x for x in chunks if x["role"]=="link"]:
        a = _as_dict(c["attrs"])
        if not (a.get("href") or "").strip():
            issues.append(("A_ACTS_BUTTON","LOW",{},c))

    # Document-level: meta & lang, skip link, landmarks
    for c in [x for x in chunks if x["role"]=="document"]:
        a = _as_dict(c["attrs"])
        if not a.get("has_title"): issues.append(("MISSING_TITLE","MEDIUM",{},c))
        if not a.get("has_viewport"): issues.append(("MISSING_VIEWPORT","LOW",{},c))
        if not a.get("has_charset"): issues.append(("MISSING_CHARSET","LOW",{},c))
        if not (a.get("html_lang") or "").strip(): issues.append(("MISSING_LANG","MEDIUM",{},c))
        if not a.get("has_skiplink"): issues.append(("MISSING_SKIPLINK","LOW",{},c))
        if not a.get("has_main"): issues.append(("MISSING_LANDMARKS","LOW",{"missing":"main"},c))
        if not a.get("has_nav"): issues.append(("MISSING_LANDMARKS","LOW",{"missing":"nav"},c))

    return issues
