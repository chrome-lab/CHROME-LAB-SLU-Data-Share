# app.py
# open terminal in ~/catkin_ws/src/ros_stt/GPT
# export GROQ_API_KEY="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"

import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- FastAPI app ---
app = FastAPI()

# --- Intent normalization ---
ALLOWED = {"wave", "highfive", "Alert", "point", "fist bump", "do nothing"}
INTENT_RE = re.compile(r"\b(wave|high\s*five|highfive|Alert|alert|point|fist[\s-]?bump|do\s*nothing)\b", re.I)

def normalize(raw: str) -> str:
    m = INTENT_RE.search(raw or "")
    if not m:
        return "do nothing"
    t = m.group(1).lower().replace("-", " ")
    if t in {"high five", "highfive"}:
        return "highfive"
    if t == "alert":
        return "Alert"
    if t in ALLOWED:
        return t
    return "do nothing"

# Opening vs farewell guardrails
RX_GREETING = re.compile(r"\b(hi|hello|hey|i\s*(?:am|'m)\b|my\s+name\s+is)\b", re.I)
RX_OPENING_COURTESY = re.compile(
    r"\b(thanks\s+for\s+having\s+me|nice\s+to\s+meet\s+you|good\s+to\s+see\s+you|great\s+to\s+be\s+here)\b", re.I
)
RX_FAREWELL = re.compile(
    r"\b(bye|goodbye|see\s*(you|ya|u)\b|take\s*care|later|farewell|good\s*night|goodnight)\b", re.I
)

# Highfive detector (covers your phrases)
RX_HIGHFIVE = re.compile(r"\bhigh[\s-]*five\b", re.I)

def postprocess(user_text: str, label_from_model: str) -> str:
    # Opening courtesy + greeting (and no explicit farewell) => wave
    if label_from_model == "fist bump":
        if RX_OPENING_COURTESY.search(user_text) and RX_GREETING.search(user_text):
            if not RX_FAREWELL.search(user_text):
                return "wave"
    # Highfive beats wave/do-nothing if we detect study/achievement signals
    if label_from_model in ("wave", "do nothing"):
        if RX_HIGHFIVE.search(user_text):
            return "highfive"
    return label_from_model

# -------- Provider client (lazy) --------
def _get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set on server")
    try:
        from groq import Groq
    except ImportError:
        raise HTTPException(status_code=500, detail="groq SDK not installed. pip install groq")
    return Groq(api_key=key)

MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # or "llama-3.1-8b-instant"

SYSTEM = (
    "Return EXACTLY ONE label (no extra words/punctuation): "
    "wave | highfive | Alert | point | fist bump | do nothing\n"
    "Rules: greeting/self-intro/opening courtesy → wave; explicit farewell → fist bump; "
    "explicit 'high five' phrase from the user →  highfive; "
    "offer help/attention → Alert; location/direction → point; else do nothing. "
    "Output: ONLY the label."
)

class Inp(BaseModel):
    text: str

@app.post("/classify")
def classify(inp: Inp):
    text = (inp.text or "")[:512]
    client = _get_client()

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
    )
    raw = resp.choices[0].message.content.strip()
    label = postprocess(text, normalize(raw))
    return {"label": label, "raw": raw}

