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
# fixer.py (replace apply_fixes with this version)
def apply_fixes(raw_html: str, issues, page_url: str = ""):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw_html or "", "lxml")

    # Index helpers
    def find_links_by_text(txt):
        out=[]
        for a in soup.find_all("a"):
            if a.get_text(strip=True)==txt:
                out.append(a)
        return out

    for (itype, _sev, details, chunk) in issues:
        attrs = _as_dict((chunk or {}).get("attrs"))
        role  = (chunk or {}).get("role")
        text  = ((chunk or {}).get("text") or "").strip()

        # 1) MISSING_ALT (existing)
        if itype == "MISSING_ALT" and role == "img":
            target_src = (attrs.get("src") or "").strip()
            candidates = []
            for img in soup.find_all("img"):
                src = (img.get("src") or img.get("data-src") or img.get("data-original") or img.get("data-lazy") or "").strip()
                if target_src and src == target_src:
                    candidates = [img]; break
                if not target_src and not (img.get("alt") or "").strip():
                    candidates.append(img)
            for img in candidates or []:
                ctx = img.parent.get_text(" ", strip=True) if img.parent else ""
                img["alt"] = generate_alt(ctx) or "Image"

        # 2) BAD_HEADING_ORDER (existing: promote one level)
        elif itype == "BAD_HEADING_ORDER" and role == "heading":
            tag = (attrs.get("tag") or "").lower()
            level = int(tag[1]) if len(tag)>1 and tag[1].isdigit() else 0
            if level > 2 and tag in {"h3","h4","h5","h6"}:
                new_tag = f"h{level-1}"
                for h in soup.find_all(tag):
                    if h.get_text(strip=True) == text:
                        h.name = new_tag
                        break

        # 3) POOR_LINK_TEXT (existing)
        elif itype == "POOR_LINK_TEXT" and role == "link":
            for a in find_links_by_text(text):
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

        # 4) LINK_NO_NAME → derive label from aria-label/title/href
        elif itype == "LINK_NO_NAME" and role == "link":
            # Prefer aria-label, else title, else slug
            for a in soup.find_all("a"):
                if (a.get("href","").strip() == attrs.get("href","").strip()) and not a.get_text(strip=True):
                    label = a.get("aria-label") or a.get("title")
                    if not label:
                        href = (a.get("href") or "").strip()
                        slug = (href.split("/")[-1] if "/" in href else href) or "link"
                        slug = slug.split("?")[0].split("#")[0]
                        label = slug.replace("-", " ").replace("_", " ").strip().title() or "Link"
                    a.string = label
                    break

        # 5) BLANK_TARGET_NO_REL → add rel=noopener noreferrer
        elif itype == "BLANK_TARGET_NO_REL" and role == "link":
            for a in soup.find_all("a"):
                if a.get("href","").strip() == attrs.get("href","").strip() and a.get("target") == "_blank":
                    rel = (a.get("rel") or [])
                    if isinstance(rel,str): rel = [rel]
                    relset = set([r.lower() for r in rel])
                    relset.update({"noopener","noreferrer"})
                    a["rel"] = " ".join(sorted(relset))
                    break

        # 6) CONTROL_NO_LABEL → add <label> or aria-label (fallback)
        elif itype == "CONTROL_NO_LABEL" and role == "control":
            tag = (attrs.get("tag") or "").lower()
            # Find the control by id/name/type
            target = None
            for el in soup.find_all(["input","select","textarea","button"]):
                if el.name == tag:
                    if attrs.get("id") and el.get("id")==attrs["id"]:
                        target = el; break
                    if attrs.get("name") and el.get("name")==attrs["name"]:
                        target = el; break
            if not target:
                continue
            if tag == "button":
                target.string = target.get_text(strip=True) or "Submit"
            else:
                # Prefer placeholder/nearby text as label; else generic
                label_text = attrs.get("placeholder") or (target.parent.get_text(" ", strip=True) if target.parent else "") or "Field"
                if not target.get("id"):
                    target["id"] = f"fld_{abs(hash(label_text))%10_000_000}"
                # Insert a label before the control
                lab = soup.new_tag("label")
                lab["for"] = target["id"]
                lab.string = label_text.strip()
                target.insert_before(lab)

        # 7) IFRAME_NO_TITLE → add title
        elif itype == "IFRAME_NO_TITLE" and role == "iframe":
            for fr in soup.find_all("iframe"):
                if not (fr.get("title") or "").strip():
                    fr["title"] = "Embedded content"

        # 8) SVG_NO_NAME → mark decorative if empty; else add aria-label
        elif itype == "SVG_NO_NAME" and role == "svg":
            for svg in soup.find_all("svg"):
                if not (svg.get_text(strip=True)):
                    svg["aria-hidden"] = "true"
                else:
                    svg["role"] = svg.get("role") or "img"
                    svg["aria-label"] = svg.get_text(strip=True)[:60]

        # 9) A_ACTS_BUTTON → convert to <button> (conservative)
        elif itype == "A_ACTS_BUTTON" and role == "link":
            for a in soup.find_all("a"):
                if not (a.get("href") or "").strip():
                    a.name = "button"
                    if not a.get_text(strip=True):
                        a.string = "Button"

        # (tabindex>0) — safer to flag only; not auto-removed globally here.

        # 10) Document-level fixes
        elif itype in {"MISSING_TITLE","MISSING_VIEWPORT","MISSING_CHARSET","MISSING_LANG","MISSING_SKIPLINK","MISSING_LANDMARKS"}:
            head = soup.find("head") or soup.new_tag("head")
            html_el = soup.find("html") or soup.new_tag("html")
            if not soup.find("head"): soup.insert(0, head)
            if not soup.find("html"): soup.insert(0, html_el)

            if itype == "MISSING_TITLE" and not head.find("title"):
                t = soup.new_tag("title"); t.string = "Accessible Page"; head.append(t)

            if itype == "MISSING_VIEWPORT" and not head.find("meta", attrs={"name":"viewport"}):
                head.append(soup.new_tag("meta", attrs={"name": "viewport", "content": "width=device-width, initial-scale=1"}))

            if itype == "MISSING_CHARSET" and not head.find("meta", attrs={"charset":True}):
                head.append(soup.new_tag("meta", charset="utf-8"))

            if itype == "MISSING_LANG" and (not html_el.get("lang")):
                html_el["lang"] = "en"

            if itype == "MISSING_SKIPLINK":
                # Insert skip link to #main at top of body
                body = soup.find("body") or soup.new_tag("body")
                if not soup.find("body"): soup.append(body)
                if not body.find("a", href="#main"):
                    a = soup.new_tag("a", href="#main")
                    a.string = "Skip to main content"
                    # simple visually-hidden style (non-breaking)
                    a["style"] = "position:absolute;left:-9999px;top:auto;width:1px;height:1px;overflow:hidden;"
                    body.insert(0, a)

            if itype == "MISSING_LANDMARKS":
                miss = (details or {}).get("missing")
                body = soup.find("body") or soup.new_tag("body")
                if not soup.find("body"): soup.append(body)
                if miss == "main" and not soup.find("main"):
                    main = soup.new_tag("main", id="main")
                    # Move the first large content block into main if possible
                    first_div = body.find("div")
                    if first_div: first_div.wrap(main)
                    else: body.insert(0, main)
                if miss == "nav" and not soup.find("nav"):
                    nav = soup.new_tag("nav"); body.insert(0, nav)

    # Normalize resource URLs & add <base>
    if page_url:
        normalize_urls(soup, page_url)

    return str(soup)
