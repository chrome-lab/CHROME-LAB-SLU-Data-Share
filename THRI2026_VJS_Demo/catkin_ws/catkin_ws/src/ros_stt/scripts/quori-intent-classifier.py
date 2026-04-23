#!/usr/bin/env python3
import os, time, requests, rospy
from std_msgs.msg import String

URL = os.getenv("INTENT_URL")  # e.g. http://127.0.0.1:8080/classify or your cloud URL
TIMEOUT = (0.5, 2.5)          # connect, read

session = requests.Session()  # keep-alive

def classify_cloud(text: str):
    r = session.post(URL, json={"text": text}, timeout=TIMEOUT)
    r.raise_for_status()
    j = r.json()
    return j.get("label","do nothing"), j.get("raw","")

class QuoriIntentProxy:
    def __init__(self):
        self.sub = rospy.Subscriber("/speech_recognition/final_result", String, self.on_text, queue_size=10)
        self.pub = rospy.Publisher("/quori/intent", String, queue_size=10)
        self.last = None

    def on_text(self, msg):
        t = (msg.data or "").strip()
        if not t or t == self.last: return
        self.last = t
        t0 = time.time()
        try:
            label, raw = classify_cloud(t)
        except Exception as e:
            rospy.loginfo(f"[CLOUD] error → do nothing: {e}")
            label, raw = "do nothing", "<error>"
        dt = time.time() - t0
        rospy.loginfo(f"[CLOUD] {dt:.3f}s user={t} raw={raw} → intent={label}")
        self.pub.publish(String(data=label))

if __name__ == "__main__":
    rospy.init_node("quori_intent_cloud_proxy", anonymous=False)
    if not URL:
        rospy.logfatal("Set INTENT_URL to your /classify endpoint (e.g. http://127.0.0.1:8080/classify)")
        raise SystemExit(1)
    QuoriIntentProxy()
    rospy.spin()


###!/usr/bin/env python3
### -*- coding: utf-8 -*-
##"""
##Quori intent classifier (ROS1) — fast, no deadline, unlimited tokens param
##
##Subscribes:
##  /speech_recognition/final_result  (std_msgs/String)
##
##Publishes:
##  /quori/intent                     (std_msgs/String)
##
##Exact labels:
##  wave | highfive | Alert | point | fist bump | do nothing
##"""
##
##import os
##import re
##import time
##from typing import Optional
##
##import rospy
##from std_msgs.msg import String
##from openai import OpenAI
##
### ============================ CONFIG ============================
##MODEL          = os.getenv("INTENT_MODEL", "gpt-5-nano")
##MAX_USER_CHARS = 512  # trim long inputs for speed without losing meaning
##_USE_COLOR     = os.getenv("INTENT_COLOR", "1") not in ("0", "false", "False")
##
### ============================ ANSI COLORS ============================
##def C(code: str) -> str: return code if _USE_COLOR else ""
##RESET = C("\033[0m"); BOLD=C("\033[1m"); DIM=C("\033[2m")
##CYAN  = C("\033[36m"); YELL=C("\033[33m"); MAG=C("\033[35m")
##GRN   = C("\033[32m"); RED =C("\033[31m")
##
##def log_llm(lat, user_text, raw, intent):
##    rospy.loginfo(
##        f"{BOLD}{CYAN}[LLM]{RESET} {DIM}{lat:.3f}s{RESET}  "
##        f"user={YELL}{user_text}{RESET}  raw={MAG}{raw}{RESET}  "
##        f"→ intent={BOLD}{GRN}{intent}{RESET}"
##    )
##
### ============================ LABELS =============================
##ALLOWED = {"wave","highfive","Alert","point","fist bump","do nothing"}
##PRIORITY = ["fist bump", "highfive", "Alert", "point", "wave", "do nothing"]
##
### ============================ PROMPT (tight + few-shot) ==========
### Kept SHORT for latency. Clear rules + minimal examples → fast & accurate.
####SYSTEM_PROMPT = (
####    "You are an intent classifier for a humanoid robot.\n"
####    "Return EXACTLY ONE of these labels (no extra words/punctuation):\n"
####    "wave | highfive | Alert | point | fist bump | do nothing\n\n"
####    "Tie-break rules:\n"
####    "- If the user both greets AND shares a major/achievement → highfive.\n"
####    "- If the user closes the interaction (goodbye/see you/thanks) → fist bump.\n\n"
####    "Definitions:\n"
####    "- wave: greetings/self-intro (hi, hello, I'm <name>, what's up).\n"
####    "- highfive: user states major/studies OR achievement/award/publication/selection.\n"
####    "- Alert: user tries to get attention or offers help (excuse me, I can help).\n"
####    "- point: user gives/asks location or direction (over there, on the table, to the left).\n"
####    "- fist bump: user ends the interaction (thanks, bye, see you).\n"
####    "- do nothing: all other normal discussion/Q&A.\n\n"
####    "Output format: ONLY the label, exactly as listed."
####)
##
##SYSTEM_PROMPT = (
##    "You are an intent classifier for a humanoid robot.\n"
##    "Return EXACTLY ONE of these labels (no extra words/punctuation):\n"
##    "wave | highfive | Alert | point | fist bump | do nothing\n\n"
##    "Tie-break rules:\n"
##    "- Greeting + achievement → highfive.\n"
##    "- Explicit farewell (bye/see you/take care/goodnight) → fist bump.\n"
##    "- Opening courtesies like “thanks for having me”, “nice to meet you”, “great to be here” are greetings → wave.\n\n"
##    "Definitions:\n"
##    "- wave: greetings/self-intro or opening courtesy (hi, hello, I'm <name>, what's up, thanks for having me, nice to meet you).\n"
##    "- highfive: user states major/studies OR achievement/award/publication/selection.\n"
##    "- Alert: user tries to get attention or offers help (excuse me, I can help).\n"
##    "- point: user gives/asks location or direction (over there, on the table, to the left).\n"
##    "- fist bump: user ends the interaction (bye, see you, take care, goodnight).\n"
##    "- do nothing: all other normal discussion/Q&A.\n\n"
##    "Output format: ONLY the label, exactly as listed."
##)
##
##
##FEWSHOT = (
##    "Examples:\n"
##    "User: hello there\n"
##    "Label: wave\n\n"
##    "User: I’m Ali from Mechanical Engineering\n"
##    "Label: wave\n\n"
##    "User: I just got first in the class!\n"
##    "Label: highfive\n\n"
##    "User: my major is Computer Science and I won a robotics prize\n"
##    "Label: highfive\n\n"
##    "User: I am focusing on algebra\n"
##    "Label: highfive\n\n"
##    "User: my favorite class is Control Systems\n"
##    "Label: highfive\n\n"
##    "User: excuse me, I can help you with that\n"
##    "Label: Alert\n\n"
##    "User: over there on the left shelf near the chair\n"
##    "Label: point\n\n"
##    "User: thanks for the help, see you later\n"
##    "Label: fist bump\n\n"
##    "User: what is the capital of France?\n"
##    "Label: do nothing\n"
##)
##
##
##def build_prompt(user_text: str) -> str:
##    return f"{SYSTEM_PROMPT}\n\n{FEWSHOT}\nNow classify:\nUser: {user_text}\nLabel:"
##
### ============================ PARSING =============================
##INTENT_REGEX = re.compile(
##    r"\b(wave|high\s*five|highfive|Alert|alert|point|fist[\s-]?bump|do\s*nothing)\b",
##    re.I
##)
##
##def _normalize_label(tok: str) -> Optional[str]:
##    if not tok: return None
##    t = tok.strip().lower().replace("-", " ")
##    if t in {"high five","highfive"}: return "highfive"
##    if t in {"alert"}: return "Alert"
##    if t in {"fist bump","fist  bump"}: return "fist bump"
##    if t in {"wave","point","do nothing"}: return t
##    return None
##
### ============================ LOCAL FALLBACK ======================
### Silent, priority-aware, and achievement-first to avoid “wave” on “hey I got first”.
##RX_WAVE = re.compile(
##    r"\b(hi|hello|hey|hiya|salam|assalam|what'?s\s*up|my\s+name\s+is)\b", re.I
##)
### High-five = studies/major/field passion/achievements/projects/publications
##RX_HIGHFIVE = re.compile(r"""
##(
##    # --- Majors / studies / year-in-major ---
##    \bi\s*(?:am|'m)\s*majoring\s+in\b
##  | \bmy\s+major\s+is\b
##  | \bi\s+study\b
##  | \bi['’]?\s*ve\s+been\s+studying\b
##  | \bi\s*(?:am|'m)\s*in\s*(?:\d+(?:st|nd|rd|th)|first|second|third|fourth|final)\s*year\s*(?:for|of)\b
##
##    # --- Favorite class / passion / focus / research area ---
##  | \bmy\s+favorite\s+(?:class|course|subject)\s+is\b
##  | \bi\s*(?:am|'m)\s*(?:focusing|focus(?:ing)?|specializing)\s+(?:in|on)\b
##  | \bi\s*love\s+(?:[A-Za-z][A-Za-z0-9&/\- ]{2,})\b    # e.g., "I love Control Systems"
##  | \bi\s*(?:am|'m)\s*passionate\s+about\b
##  | \bi\s*(?:am|'m)\s*from\s+the?\s+(?:lab|department|dept\.?|faculty|school)\b
##  | \bmy\s+research\b
##  | \bresearch(?:ing)?\s+(?:on|in)\b
##
##    # --- Projects / capstone / thesis / senior design ---
##  | \bi\s+just\s+finished\s+(?:a\s+)?project\s+(?:in|on|about)\b
##  | \bi\s*(?:am|'m)\s*(?:working|writing)\s+on\b.*\b(capstone|thesis|senior\s+design\s+project|fyp)\b
##  | \bi\s*(?:am|'m)\s*(?:excited|starting)\b.*\b(senior\s+design\s+project|capstone|fyp)\b
##  | \bcapstone\b|\bthesis\b|\bsenior\s+design\s+project\b|\bFYP\b
##
##    # --- Teams / clubs / labs / departments ---
##  | \bi\s*(?:am|'m)\s*part\s+of\s+the?\s+(?:team|club|lab|society|chapter|group)\b
##  | \bi\s*(?:am|'m)\s+from\s+the?\s+(?:lab|department|dept\.?|faculty|school)\b
##
##    # --- Time-in-study phrasing ---
##  | \bi['’]?\s*ve\s+been\s+studying\b.*\bfor\b.*\b(?:\d+\s*(?:years?|months?)|a\s+year|a\s+while)\b
##
##    # --- Publications / papers / acceptance ---
##  | \bi\s+just\s+published\s+my\s+(?:first|1st)\s+paper\b
##  | \bpaper\s+accepted\b
##  | \b(?:journal|conference)\s+paper\b
##  | \baccepted\s+to\b.*\b(?:conference|journal)\b
##)
##""", re.I | re.X)
##
##RX_ALERT = re.compile(
##    r"\b(excuse\s*me|attention|listen|over here|heads up|can i help|let me help|i can help|i can assist|i'?m here to help)\b", re.I
##)
##RX_POINT = re.compile(
##    r"\b(where('?| i)?s|location|over there|right there|on (the )?table|to the (left|right)|"
##    r"by the|near the|next to|on the shelf|see that|it'?s there)\b", re.I
##)
##RX_FIST = re.compile(
##    r"\b(bye|goodbye|see\s*(you|ya)|take\s*care|later|thanks[,! ]*bye|farewell|good\s*night|goodnight|"
##    r"that'?s all|we'?re done|see you next time)\b", re.I
##)
##
##def detect_features(text: str) -> dict:
##    return {
##        "fist bump": bool(RX_FIST.search(text)),
##        "highfive": bool(RX_HIGHFIVE.search(text)),
##        "Alert": bool(RX_ALERT.search(text)),
##        "point": bool(RX_POINT.search(text)),
##        "wave": bool(RX_WAVE.search(text)),
##        "do nothing": False,
##    }
##
##def choose_by_priority(flags: dict) -> str:
##    for label in PRIORITY:
##        if label != "do nothing" and flags.get(label, False):
##            return label
##    return "do nothing"
##
##def fallback_classify(text: str) -> str:
##    flags = detect_features(text)
##    # greeting + achievement → highfive
##    if flags["highfive"]:
##        flags["wave"] = False
##    # closing wins
##    if flags["fist bump"]:
##        return "fist bump"
##    return choose_by_priority(flags)
##
### ============================ OPENAI CLIENT =======================
##CLIENT = OpenAI(api_key="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")
##
##def model_classify(user_text: str) -> str:
##    """
##    Single Responses API call. No deadline, no max_output_tokens (unlimited on our side).
##    Returns the raw model text (may include extra words).
##    """
##    clipped = user_text[:MAX_USER_CHARS]
##    prompt = build_prompt(clipped)
##
##    # Keep it deterministic & tiny output for speed.
##    # Note: We intentionally omit max_output_tokens -> API decides; we keep it “unlimited” here.
##    resp = CLIENT.responses.create(
##        model=MODEL,
##        input=prompt,
##        #temperature=0,
##    )
##    # Prefer the convenience accessor
##    try:
##        return (resp.output_text or "").strip()
##    except Exception:
##        # Robust extraction for SDK variations
##        if getattr(resp, "output", None):
##            for item in resp.output:
##                try:
##                    t = getattr(item, "content", [])[0].get("text", {}).get("value", "")
##                    if t: return t.strip()
##                except Exception:
##                    pass
##        return ""  # let fallback handle it silently
##
##def classify(user_text: str) -> (str, float, str):
##    """
##    Returns (intent, latency_s, raw_reply).
##    If parsing fails or API errors, uses local fallback quietly.
##    """
##    start = time.perf_counter()
##    raw = ""
##    try:
##        raw = model_classify(user_text)
##    except Exception as e:
##        # No noisy WARNs; STT/NET hiccups are common in robotics.
##        rospy.logdebug(f"[OpenAI] API error → fallback: {e}")
##        intent = fallback_classify(user_text)
##        return intent, time.perf_counter() - start, "<error>"
##
##    # Parse & normalize
##    m = INTENT_REGEX.search(raw or "")
##    intent = _normalize_label(m.group(1)) if m else None
##
##    # Guardrails: upgrade weak labels if strong cues detected locally
##    if intent in (None, "wave", "do nothing"):
##        flags = detect_features(user_text)
##        if flags["fist bump"]:
##            return "fist bump", time.perf_counter() - start, raw
##        if flags["highfive"]:
##            return "highfive", time.perf_counter() - start, raw
##        if intent in (None, "do nothing"):
##            return choose_by_priority(flags), time.perf_counter() - start, raw
##
##    if intent in ALLOWED:
##        return intent, time.perf_counter() - start, raw
##
##    # Fallback for unrecognized output
##    return fallback_classify(user_text), time.perf_counter() - start, raw or "<empty>"
##
### ============================ ROS NODE ============================
##class QuoriIntentNode:
##    def __init__(self):
##        self.input_topic  = rospy.get_param("~input_topic",  "/speech_recognition/final_result")
##        self.output_topic = rospy.get_param("~output_topic", "/quori/intent")
##        self.pub = rospy.Publisher(self.output_topic, String, queue_size=10)
##        self.sub = rospy.Subscriber(self.input_topic, String, self._on_text, queue_size=10)
##        self._last_text = None
##        rospy.loginfo("QuoriIntentNode ready. Subscribing to %s → publishing %s",
##                      self.input_topic, self.output_topic)
##
##    def _on_text(self, msg: String):
##        user_text = (msg.data or "").strip()
##        if not user_text:
##            return
##        if user_text == self._last_text:
##            rospy.logdebug("Duplicate text ignored: %s", user_text)
##            return
##        self._last_text = user_text
##
##        intent, latency, raw = classify(user_text)
##        log_llm(latency, user_text, raw, intent)
##        self.pub.publish(String(data=intent))
##        rospy.loginfo(f"{BOLD}{GRN}Intent published{RESET}: {intent}")
##
##def main():
##    rospy.init_node("quori_intent_classifier", anonymous=False)
##    QuoriIntentNode()
##    rospy.spin()
##
##if __name__ == "__main__":
##    main()
##
