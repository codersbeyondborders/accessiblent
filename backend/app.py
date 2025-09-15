# app.py
import os
import json
import datetime
import urllib.parse

import httpx
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

from db import init_pool, q
from a11y import extract_chunks, audit
from fixer import apply_fixes

from typing import List, Optional

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

app = FastAPI(title="Accessiblent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten to your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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



# ---------- routes ----------
@app.get("/health")
def health():
    q("SELECT 1")
    return {"ok": True}

@app.get("/output/{page_id}", response_class=HTMLResponse)
def output_html(page_id: int):
    row = q("SELECT fixed_html FROM page WHERE id=%s", (page_id,))
    if not row or not row[0]["fixed_html"]:
        raise HTTPException(404, "No fixed HTML yet.")
    return HTMLResponse(content=row[0]["fixed_html"], status_code=200)

@app.post("/process")
async def process(
    url: str = Query(..., min_length=5),
    mode: str = Query("fast")
):
    """
    One-click pipeline:
    1) fetch HTML, 2) save page+chunks, 3) audit, 4) fix & normalize for standalone viewing,
    5) embed chunks for RAG, 6) return page_id + short summary.
    """
    # 1) fetch HTML
    try:
        html = await fetch_html(url)
    except Exception as e:
        raise HTTPException(400, f"Failed to fetch: {e}")

    domain = urllib.parse.urlparse(url).netloc

    # 2) create page
    page_id = q(
        "INSERT INTO page (url, domain, raw_html, status, created_at) VALUES (%s,%s,%s,%s,%s)",
        (url, domain, html, "NEW", datetime.datetime.utcnow())
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

    return {"page_id": page_id, "summary": summary, "issues": len(issues)}

@app.post("/chat/{page_id}")
def chat_page(page_id: int, body: dict = Body(...)):
    """
    Retrieval-augmented Q/A over this page:
    - embed the question
    - KNN over chunk.embedding (cosine)
    - answer grounded in top chunks
    """
    question = (body.get("question") or "").strip()
    if not question:
        raise HTTPException(400, "Missing question")

    if not openai_client:
        return {"answer": "Chat is disabled (no API key configured)."}

    # a) embed query
    qvec = openai_client.embeddings.create(model=EMBED_MODEL, input=question).data[0].embedding
    qvec_lit = json.dumps(qvec)  # pass as JSON string literal for TiDB VECTOR

    # b) retrieve top-k chunks for this page (note: WHERE can inhibit index; OK for our scale)
    hits = q("""
        SELECT text, VEC_COSINE_DISTANCE(embedding, %s) AS distance
        FROM chunk
        WHERE page_id = %s
        ORDER BY distance
        LIMIT 8
    """, (qvec_lit, page_id))

    context = "\n\n".join([h["text"] or "" for h in hits])[:8000]
    if not context.strip():
        return {"answer": "I couldn’t find content to answer that on this page."}

    # c) answer with LLM
    prompt = (
        "Answer the user's question using only the provided page content.\n\n"
        f"CONTENT:\n{context}\n\nQUESTION: {question}\n\nANSWER:"
    )
    r = openai_client.responses.create(
        model=CHAT_MODEL,
        input=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_output_tokens=400,
    )
    return {"answer": (r.output_text or '').strip()}
