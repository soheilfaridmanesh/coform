import json
import os
from io import BytesIO

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="Coform — AI Co-Design Studio", page_icon="C", layout="wide", initial_sidebar_state="collapsed")

st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

:root { --ink:#111; --muted:#70706a; --line:#deded8; --paper:#fff; --soft:#f6f6f3; }

/* Full-screen, non-scrollable canvas */
html, body, [data-testid="stAppViewContainer"], [data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] > .main > .block-container {
    width:100%; height:100vh !important; max-height:100vh !important;
    overflow:hidden !important;
}
html, body, [class*="css"], button, input, textarea, select { font-family:'Outfit', sans-serif !important; }
body { overflow:hidden !important; }
.stApp { background:var(--paper); color:var(--ink); overflow:hidden !important; }
.block-container { max-width:1180px; height:100vh !important; max-height:100vh !important; padding:16px 28px 18px !important; margin:0 auto; overflow:hidden !important; box-sizing:border-box; }
#MainMenu, footer, header[data-testid="stHeader"] { display:none !important; }

/* Header */
.topbar { height:42px; border-bottom:1px solid var(--line); display:flex; align-items:center; justify-content:center; position:relative; }
.wordmark { font-size:30px; line-height:1; font-weight:600; letter-spacing:-.055em; color:#111; }
.beta { position:absolute; left:calc(50% + 47px); top:4px; font-size:10px; line-height:1; color:#777; letter-spacing:.02em; }
.progress { display:flex; align-items:center; justify-content:center; gap:8px; height:24px; margin-top:8px; }
.progress .node { font-size:11px; color:#b1b0aa; white-space:nowrap; letter-spacing:.01em; }
.progress .node.active, .progress .node.done { color:#111; }
.progress .line { width:24px; height:1px; background:#e8e8e3; }
.progress .line.done { background:#111; }

/* One viewport per stage */
.st-key-screen {
    height:calc(100vh - 100px) !important;
    max-height:calc(100vh - 100px) !important;
    overflow-y:auto !important;
    overflow-x:hidden !important;
    display:flex !important; flex-direction:column !important; justify-content:flex-start !important;
    box-sizing:border-box; padding:72px 0 26px !important; width:100%;
}
.st-key-screen > div[data-testid="stVerticalBlock"] {
    display:flex !important; flex-direction:column !important; align-items:center !important;
    width:100%; text-align:center;
}
/* Kill Streamlit's default gaps between elements so only our own spacing shows */
[data-testid="stVerticalBlock"] { gap:0 !important; }
[data-testid="stElementContainer"] { margin:0 !important; }
.eyebrow { font-size:12px; line-height:1.2; letter-spacing:.13em; text-transform:uppercase; color:#777; margin:0 0 14px; }
.question { width:min(900px,100%) !important; font-size:clamp(42px,5.2vw,70px); line-height:.98; letter-spacing:-.06em; font-weight:400; margin:0 auto !important; color:#111 !important; text-align:center !important; }
.subcopy { width:min(600px,100%) !important; color:#666 !important; font-size:16px; line-height:1.45; margin:22px auto 0 !important; text-align:center !important; }
.st-key-choice_wrap { width:100%; margin:44px auto 0 !important; text-align:center; }
.choice-label { font-size:12px; color:#777; letter-spacing:.11em; text-transform:uppercase; margin-bottom:26px; text-align:center; }

/* Equal-size square option tiles, tightly and evenly spaced */
.st-key-choice_grid { width:fit-content; max-width:100%; margin:0 auto !important; }
.st-key-choice_grid div[data-testid="stHorizontalBlock"] { justify-content:center !important; gap:10px !important; }
.st-key-choice_grid div[data-testid="stColumn"] { width:156px !important; flex:0 0 156px !important; min-width:156px !important; max-width:156px !important; }
.st-key-choice_grid div[data-testid="stButton"] { display:flex; justify-content:center; }
.st-key-choice_grid > div[data-testid="stLayoutWrapper"] + div[data-testid="stLayoutWrapper"] { margin-top:10px !important; }
.st-key-choice_grid div[data-testid="stButton"] > button {
    width:156px !important; min-width:156px !important; max-width:156px !important;
    height:156px !important; min-height:156px !important; max-height:156px !important;
    aspect-ratio:1 / 1 !important; padding:18px 14px !important;
    border-radius:14px !important; border:1px solid #c8c8c2 !important;
    background:#fff !important; color:#111 !important; box-shadow:none !important;
    font-size:15px !important; line-height:1.25 !important; font-weight:400 !important;
    white-space:normal !important;
}
.st-key-choice_grid div[data-testid="stButton"] > button:hover { border-color:#111 !important; background:#fafaf8 !important; }
.st-key-choice_grid div[data-testid="stButton"] > button[kind="primary"] { background:#111 !important; border-color:#111 !important; color:#fff !important; }

/* Circular action buttons, centered as a block */
.st-key-actions { margin:32px auto 0 !important; width:fit-content !important; }
.st-key-actions div[data-testid="stHorizontalBlock"] { justify-content:center !important; align-items:center !important; gap:16px !important; width:fit-content !important; margin:0 auto !important; }
.st-key-actions div[data-testid="stColumn"] { width:fit-content !important; flex:0 0 auto !important; min-width:0 !important; display:flex !important; align-items:center !important; }
.st-key-actions div[data-testid="stButton"] { display:flex; justify-content:center; }
.st-key-actions div[data-testid="stButton"] > button {
    width:120px !important; min-width:120px !important; max-width:120px !important;
    height:120px !important; min-height:120px !important; max-height:120px !important;
    aspect-ratio:1 / 1 !important; padding:10px 18px !important;
    border-radius:50% !important; border:1px solid #111 !important;
    font-size:13px !important; font-weight:500 !important; line-height:1.25 !important;
    white-space:normal !important; box-shadow:none !important;
}
.st-key-actions div[data-testid="stButton"] > button[kind="primary"] { background:#111 !important; color:#fff !important; }
.st-key-actions div[data-testid="stButton"] > button[kind="secondary"] {
    width:64px !important; min-width:64px !important; max-width:64px !important;
    height:64px !important; min-height:64px !important; max-height:64px !important;
    font-size:16px !important; padding:0 !important;
}

/* Inputs */
.st-key-inputbox { width:min(650px,100%); margin:36px auto 0 !important; }
.st-key-inputbox div[data-testid="stTextArea"], .st-key-inputbox div[data-testid="stTextInput"] { width:100%; }
.st-key-inputbox textarea, .st-key-inputbox input {
    border-radius:8px !important; border:1px solid #c8c8c2 !important; background:#fff !important;
    color:#111 !important; font-size:16px !important; line-height:1.5 !important; text-align:center !important;
    box-shadow:none !important;
}
.st-key-inputbox textarea:focus, .st-key-inputbox input:focus { border-color:#111 !important; box-shadow:0 0 0 1px #111 !important; }

/* Reference upload */
.st-key-uploadbox { width:min(700px,100%); margin:0 auto !important; }
.st-key-uploadbox [data-testid="stFileUploader"] { font-size:14px; }
.st-key-uploadbox [data-testid="stFileUploaderDropzone"] { border:1px dashed #c6c6c0 !important; border-radius:8px !important; background:#fff !important; }
.ref-thumbs { display:flex; justify-content:center; gap:8px; margin-top:12px; }
.ref-thumb { width:72px; height:72px; object-fit:cover; border-radius:6px; border:1px solid #e2e2dc; }

/* Direction */
.summary { width:min(700px,100%); border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:16px 0; margin:18px auto 0; font-size:16px; line-height:1.5; text-align:center; }
.signal-row { display:flex; justify-content:center; flex-wrap:wrap; gap:7px; margin-top:11px; }
.signal { border:1px solid #d1d1cc; border-radius:6px; padding:7px 10px; font-size:13px; }

/* Design DNA */
.dna { width:min(900px,100%); background:#111; color:#fff; border-radius:10px; padding:17px 20px; margin:18px auto 0; text-align:center; box-sizing:border-box; }
.dna-title { font-size:11px; color:#aaa; letter-spacing:.12em; text-transform:uppercase; }
.dna-head { font-size:22px; letter-spacing:-.035em; margin-top:4px; }
.dna-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:13px; margin-top:14px; }
.dna-item strong { display:block; font-size:10px; color:#999; letter-spacing:.1em; text-transform:uppercase; margin-bottom:4px; }
.dna-item span { color:#f2f2ef; font-size:13px; line-height:1.3; }

/* Text-only concept grid — no paid image generation */
.concept-grid { width:min(980px,100%); display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin:18px auto 0; }
.concept-card { border:1px solid #d7d7d1; border-radius:10px; padding:18px; text-align:center; box-sizing:border-box; min-height:190px; margin-top:16px; }
.concept-number { font-size:11px; color:#777; letter-spacing:.12em; text-transform:uppercase; }
.concept-title { font-size:21px; letter-spacing:-.035em; margin-top:6px; }
.concept-tagline { font-size:14px; color:#666; line-height:1.4; margin-top:6px; }
.concept-detail { font-size:13px; line-height:1.4; margin-top:10px; color:#333; }

.feedback-box { width:min(650px,100%); margin:18px auto 0; text-align:center; }
.feedback-label { font-size:12px; letter-spacing:.11em; text-transform:uppercase; color:#777; margin-bottom:9px; }

.credit { position:fixed; left:0; right:0; bottom:9px; text-align:center; font-size:12px; line-height:1.4; color:#999; pointer-events:none; }
.credit strong { color:#555; font-weight:500; }

/* Keep Streamlit messages readable without adding layout height */
[data-testid="stAlert"] { max-width:700px; margin:8px auto !important; font-size:13px !important; }

@media (max-width:800px) {
    .block-container { padding:12px 16px 16px !important; }
    .wordmark { font-size:27px; }
    .beta { left:calc(50% + 43px); }
    .progress { gap:4px; }
    .progress .line { width:8px; }
    .progress .node { font-size:9px; }
    .st-key-screen { height:calc(100vh - 92px) !important; max-height:calc(100vh - 92px) !important; padding:60px 0 22px !important; }
    .question { font-size:43px; }
    .subcopy { font-size:15px; }
    .st-key-choice_grid div[data-testid="stButton"] > button { width:132px !important; min-width:132px !important; max-width:132px !important; height:132px !important; min-height:132px !important; max-height:132px !important; }
    .st-key-choice_grid div[data-testid="stColumn"] { width:132px !important; flex:0 0 132px !important; min-width:132px !important; max-width:132px !important; }
    .st-key-actions div[data-testid="stButton"] > button { width:100px !important; min-width:100px !important; max-width:100px !important; height:100px !important; min-height:100px !important; max-height:100px !important; }
    .dna-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
    .concept-grid { grid-template-columns:1fr; max-width:460px; }
}
</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "stage": 1,
        "brief_step": 0,
        "project_type": None,
        "brief": "",
        "inspiration_mode": None,
        "inspiration_analysis": None,
        "questions": None,
        "question_index": 0,
        "answers": {},
        "direction": None,
        "concepts": None,
        "selected_concept": None,
        "revision": None,
        "dna": None,
        "uploaded_images": [],
        "ref_question_index": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

SYSTEM = """You are a senior product designer and creative director acting as a design collaborator.
The human designer is always the source of truth for taste and intent.
Never invent a preference that the designer has not supplied.
Separate observable signals from explicit choices and assumptions.
Ask only the minimum questions needed to reduce meaningful uncertainty.
Prefer concrete design decisions over generic adjectives.
When feedback is given, retain what the designer liked, change what they rejected, and update a compact Design DNA profile.
Return one valid JSON object whenever JSON is requested. Never return multiple JSON objects, commentary, or markdown fences."""


def get_api_key():
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def client():
    key = get_api_key()
    return genai.Client(api_key=key) if key else None


def parse_json_object(text):
    if not text:
        raise ValueError("The AI returned an empty response.")
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "", 1).replace("```", "", 1).strip()
    start = cleaned.find("{")
    if start == -1:
        raise ValueError("The AI response did not contain a JSON object.")
    obj, _ = json.JSONDecoder().raw_decode(cleaned[start:])
    if not isinstance(obj, dict):
        raise ValueError("The AI response was not a JSON object.")
    return obj


def call_ai(prompt, images=None):
    c = client()
    if not c:
        raise RuntimeError("Missing GEMINI_API_KEY. Set it in Terminal before running Coform.")
    parts = [types.Part.from_text(text=prompt)]
    for img in images or []:
        buf = BytesIO()
        img.save(buf, format="PNG")
        parts.append(types.Part.from_bytes(data=buf.getvalue(), mime_type="image/png"))
    model = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    response = c.models.generate_content(
        model=model,
        contents=parts,
        config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.55, response_mime_type="application/json"),
    )
    return parse_json_object(response.text)


def _img_to_b64(img):
    import base64
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def analyze_references(images):
    prompt = """Analyze these design references as a visual inspiration set.
Describe observable signals, not inferred personal preferences.
Return exactly one JSON object:
{"summary":"1-2 sentence synthesis","signals":{"typography":["..."],"layout":["..."],"color":["..."],"imagery":["..."],"components":["..."],"motion":["..."]},"questions":["one or two specific decisions the designer still needs to make"]}"""
    return call_ai(prompt, images)


def make_questions(project_type, brief):
    prompt = f"""We are starting a new design session.
Project type: {project_type}
Brief: {brief}
No visual inspiration has been provided.
Create 4 high-value design questions. Each question must have 3-5 concrete options.
Cover emotional tone, composition/layout, visual priority, density or interaction, and what to avoid.
Do not infer the preferred answers. Make options concise and mutually understandable.
Return exactly one JSON object: {{"questions":[{{"id":"tone","question":"...","options":["..."],"type":"single"}}]}}"""
    return call_ai(prompt)


def make_direction(project_type, brief, inspiration, answers):
    prompt = f"""Create a working design direction using only the information below.
Project: {project_type}
Brief: {brief}
Observed inspiration signals: {json.dumps(inspiration, ensure_ascii=False)}
Explicit designer choices: {json.dumps(answers, ensure_ascii=False)}
Return exactly one JSON object:
{{"concept":"short direction name","thesis":"2-3 sentences","visual_language":["..."],"layout":["..."],"typography":["..."],"color":["..."],"imagery":["..."],"motion":["..."],"avoid":["..."],"dna":{{"layout":"...","density":"...","typography":"...","color":"...","imagery":"...","motion":"...","avoid":["..."]}}}}"""
    return call_ai(prompt)


def make_concepts(direction, brief):
    prompt = f"""Create 3 distinct design concept directions for this brief.
Brief: {brief}
Design direction: {json.dumps(direction, ensure_ascii=False)}
Each concept should make a different composition or emphasis choice while respecting the same Design DNA.
These are concise concept descriptions for a product designer to react to, not final copy.
Return exactly one JSON object:
{{"concepts":[
{{"name":"...","tagline":"...","layout":"...","hero":"...","content_hierarchy":["..."],"interaction":"...","why":"..."}},
{{"name":"...","tagline":"...","layout":"...","hero":"...","content_hierarchy":["..."],"interaction":"...","why":"..."}},
{{"name":"...","tagline":"...","layout":"...","hero":"...","content_hierarchy":["..."],"interaction":"...","why":"..."}}
]}}"""
    result = call_ai(prompt)
    concepts = result.get("concepts")
    if not isinstance(concepts, list) or len(concepts) < 3:
        raise ValueError("The AI returned fewer than three concept directions. Please try again.")
    return concepts[:3]


def revise(direction, selected, feedback, dna):
    prompt = f"""Revise a design concept based on explicit human feedback.
Current direction: {json.dumps(direction, ensure_ascii=False)}
Selected concept: {json.dumps(selected, ensure_ascii=False)}
Designer feedback: {feedback}
Current Design DNA: {json.dumps(dna, ensure_ascii=False)}
Return exactly one JSON object:
{{"summary":"what changed","changed":["..."],"kept":["..."],"updated_concept":{{"name":"...","tagline":"...","layout":"...","hero":"...","content_hierarchy":["..."],"interaction":"...","why":"..."}},"dna":{{"layout":"...","density":"...","typography":"...","color":"...","imagery":"...","motion":"...","avoid":["..."]}}}}"""
    return call_ai(prompt)


def progress_bar(stage):
    labels = ["01 Brief", "02 Inspiration", "03 Direction", "04 Studio", "05 Co-design"]
    parts = []
    for index, label in enumerate(labels, 1):
        state = "active" if index == stage else ("done" if index < stage else "")
        parts.append(f'<span class="node {state}">{label}</span>')
        if index < len(labels):
            parts.append(f'<span class="line {"done" if index < stage else ""}"></span>')
    return "".join(parts)


def choice_grid(options, state_key, columns=3, key_prefix="choice"):
    current = st.session_state.get(state_key)
    with st.container(key="choice_grid"):
        for row_start in range(0, len(options), columns):
            row_options = options[row_start:row_start + columns]
            cols = st.columns(columns, gap="small")
            for i in range(columns):
                if i >= len(row_options):
                    continue
                option = row_options[i]
                index = row_start + i
                with cols[i]:
                    selected = current == option
                    if st.button(option, key=f"{key_prefix}_{state_key}_{index}", type="primary" if selected else "secondary"):
                        st.session_state[state_key] = option
                        st.rerun()
    return st.session_state.get(state_key)


def actions():
    return st.container(key="actions")


def reset_session():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def api_error(exc):
    st.error(f"AI request failed: {exc}")


# Header
st.markdown(
    f'<div class="topbar"><div class="wordmark">Coform</div><span class="beta">[Beta]</span></div>'
    f'<div class="progress">{progress_bar(st.session_state.stage)}</div>',
    unsafe_allow_html=True,
)

# Stage 1 — brief
if st.session_state.stage == 1:
    with st.container(key="screen"):
        if st.session_state.brief_step == 0:
            st.markdown('<h1 class="question">What are we designing?</h1>', unsafe_allow_html=True)
            st.markdown('<div class="subcopy">Start with the thing itself. Coform will not assume a visual style.</div>', unsafe_allow_html=True)
            with st.container(key="choice_wrap"):
                st.markdown('<div class="choice-label">Choose one</div>', unsafe_allow_html=True)
                selected = choice_grid(["Website", "Landing page", "Mobile app", "Dashboard", "E-commerce", "Brand experience", "Other"], "project_type", columns=4, key_prefix="project")
            with actions():
                if st.button("Continue →", type="primary", disabled=not selected):
                    st.session_state.brief_step = 1
                    st.rerun()
        else:
            st.markdown('<h1 class="question">Tell us what you are making.</h1>', unsafe_allow_html=True)
            st.markdown('<div class="subcopy">One or two sentences are enough. Coform will ask for direction separately.</div>', unsafe_allow_html=True)
            with st.container(key="inputbox"):
                brief = st.text_area("Brief", value=st.session_state.brief, placeholder="A website for a premium boutique hotel that wants more direct bookings.", height=110, label_visibility="collapsed")
            with actions():
                back_col, continue_col = st.columns(2, gap="small")
                with back_col:
                    if st.button("←", key="back_brief2"):
                        st.session_state.brief_step = 0
                        st.rerun()
                with continue_col:
                    if st.button("Continue →", type="primary", disabled=not brief.strip()):
                        st.session_state.brief = brief.strip()
                        st.session_state.stage = 2
                        st.rerun()

# Stage 2 — inspiration
elif st.session_state.stage == 2:
    with st.container(key="screen"):
        if st.session_state.inspiration_mode is None:
            st.markdown('<h1 class="question">Do you have visual references?</h1>', unsafe_allow_html=True)
            st.markdown('<div class="subcopy">If you do, Coform will observe them. If you do not, it will ask for direction instead of guessing.</div>', unsafe_allow_html=True)
            with st.container(key="choice_wrap"):
                st.markdown('<div class="choice-label">Choose one</div>', unsafe_allow_html=True)
                choice = choice_grid(["I have references", "I don't have references"], "inspiration_choice", columns=2, key_prefix="inspiration")
            with actions():
                back_col, continue_col = st.columns(2, gap="small")
                with back_col:
                    if st.button("←", key="back_inspchoice"):
                        st.session_state.brief_step = 1
                        st.session_state.stage = 1
                        st.rerun()
                with continue_col:
                    if st.button("Continue →", type="primary", disabled=not choice):
                        st.session_state.inspiration_mode = "references" if choice == "I have references" else "questions"
                        if st.session_state.inspiration_mode == "questions":
                            if not get_api_key():
                                st.error("Set GEMINI_API_KEY in Terminal first.")
                            else:
                                with st.spinner("Preparing a few focused questions…"):
                                    try:
                                        st.session_state.questions = make_questions(st.session_state.project_type, st.session_state.brief)["questions"]
                                        st.session_state.question_index = 0
                                        st.session_state.stage = 3
                                        st.rerun()
                                    except Exception as exc:
                                        api_error(exc)
                        else:
                            st.rerun()
        else:
            st.markdown('<h1 class="question">Show me what you like.</h1>', unsafe_allow_html=True)
            st.markdown('<div class="subcopy">Upload a small set of references. Coform will look for visual signals, not assume your taste.</div>', unsafe_allow_html=True)
            with st.container(key="uploadbox"):
                uploaded = st.file_uploader("Upload references", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True, label_visibility="collapsed")
            if uploaded:
                imgs = []
                for file in uploaded[:6]:
                    try:
                        imgs.append(Image.open(file).convert("RGB"))
                    except Exception:
                        pass
                st.session_state.uploaded_images = imgs
                if imgs:
                    thumbs = ''.join(f'<img class="ref-thumb" src="data:image/png;base64,{_img_to_b64(img)}">' for img in imgs)
                    st.markdown(f'<div class="ref-thumbs">{thumbs}</div>', unsafe_allow_html=True)
            with actions():
                back_col, continue_col = st.columns(2, gap="small")
                with back_col:
                    if st.button("←", key="back_upload"):
                        st.session_state.inspiration_mode = None
                        st.rerun()
                with continue_col:
                    if st.button("Read references →", type="primary", disabled=not st.session_state.uploaded_images):
                        if not get_api_key():
                            st.error("Set GEMINI_API_KEY in Terminal first.")
                        else:
                            with st.spinner("Reading the visual signals…"):
                                try:
                                    st.session_state.inspiration_analysis = analyze_references(st.session_state.uploaded_images)
                                    st.session_state.ref_question_index = 0
                                    st.session_state.stage = 3
                                    st.rerun()
                                except Exception as exc:
                                    api_error(exc)

# Stage 3 — direction questions
elif st.session_state.stage == 3:
    if st.session_state.inspiration_mode == "references":
        analysis = st.session_state.inspiration_analysis or {}
        questions = analysis.get("questions", [])
        idx = st.session_state.ref_question_index
        if idx < len(questions):
            with st.container(key="screen"):
                st.markdown(f'<h1 class="question">{questions[idx]}</h1>', unsafe_allow_html=True)
                st.markdown('<div class="subcopy">Your references give Coform a starting point. This answer closes one remaining gap.</div>', unsafe_allow_html=True)
                with st.container(key="inputbox"):
                    answer = st.text_area("Answer", key=f"ref_answer_{idx}", placeholder="Tell Coform what you want.", height=105, label_visibility="collapsed")
                with actions():
                    back_col, continue_col = st.columns(2, gap="small")
                    with back_col:
                        if st.button("←", key="back_refq"):
                            if idx == 0:
                                st.session_state.stage = 2
                            else:
                                st.session_state.ref_question_index = idx - 1
                            st.rerun()
                    with continue_col:
                        if st.button("Continue →", type="primary", disabled=not answer.strip()):
                            st.session_state.answers[f"reference_{idx}"] = answer.strip()
                            st.session_state.ref_question_index += 1
                            st.rerun()
        else:
            with st.container(key="screen"):
                st.markdown('<h1 class="question">Here is what I found.</h1>', unsafe_allow_html=True)
                st.markdown(f'<div class="summary">{analysis.get("summary", "The references establish an initial visual direction.")}</div>', unsafe_allow_html=True)
                with actions():
                    back_col, continue_col = st.columns(2, gap="small")
                    with back_col:
                        if st.button("←", key="back_refsum"):
                            st.session_state.ref_question_index = max(0, len(questions) - 1)
                            st.rerun()
                    with continue_col:
                        if st.button("Build my direction →", type="primary"):
                            try:
                                direction = make_direction(st.session_state.project_type, st.session_state.brief, analysis, st.session_state.answers)
                                st.session_state.direction = direction
                                st.session_state.dna = direction.get("dna", {})
                                st.session_state.stage = 4
                                st.rerun()
                            except Exception as exc:
                                api_error(exc)
    else:
        questions = st.session_state.questions or []
        idx = st.session_state.question_index
        q = questions[idx] if idx < len(questions) else None
        if q:
            with st.container(key="screen"):
                st.markdown(f'<h1 class="question">{q.get("question", "What do you prefer?")}</h1>', unsafe_allow_html=True)
                st.markdown('<div class="subcopy">There is no default answer. Choose what feels right for this project.</div>', unsafe_allow_html=True)
                with st.container(key="choice_wrap"):
                    st.markdown('<div class="choice-label">Choose one</div>', unsafe_allow_html=True)
                    q_id = q.get("id", str(idx))
                    selected = choice_grid(q.get("options", []), f"answer_{q_id}", columns=min(4, max(1, len(q.get("options", [])))), key_prefix="answer")
                    if selected:
                        st.session_state.answers[q_id] = selected
                with actions():
                    back_col, continue_col = st.columns(2, gap="small")
                    with back_col:
                        if st.button("←", key="back_mcq"):
                            if idx == 0:
                                st.session_state.inspiration_mode = None
                                st.session_state.stage = 2
                            else:
                                st.session_state.question_index = idx - 1
                            st.rerun()
                    with continue_col:
                        label = "Build my direction →" if idx == len(questions) - 1 else "Continue →"
                        if st.button(label, type="primary", disabled=not selected):
                            if idx == len(questions) - 1:
                                try:
                                    direction = make_direction(st.session_state.project_type, st.session_state.brief, {}, st.session_state.answers)
                                    st.session_state.direction = direction
                                    st.session_state.dna = direction.get("dna", {})
                                    st.session_state.stage = 4
                                    st.rerun()
                                except Exception as exc:
                                    api_error(exc)
                            else:
                                st.session_state.question_index += 1
                                st.rerun()

# Stage 4 — text concepts only
elif st.session_state.stage == 4:
    direction = st.session_state.direction or {}
    with st.container(key="screen"):
        st.markdown(f'<h1 class="question">{direction.get("concept", "Your design direction")}</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="subcopy">{direction.get("thesis", "A working direction built from your choices.")}</div>', unsafe_allow_html=True)
        dna = st.session_state.dna or {}
        dna_html = ''.join(f'<div class="dna-item"><strong>{key}</strong><span>{" · ".join(value) if isinstance(value, list) else value}</span></div>' for key, value in dna.items())
        st.markdown(f'<div class="dna"><div class="dna-title">Design DNA</div><div class="dna-head">The rules we agreed on.</div><div class="dna-grid">{dna_html}</div></div>', unsafe_allow_html=True)
        if st.session_state.concepts is None:
            with actions():
                back_col, gen_col = st.columns(2, gap="small")
                with back_col:
                    if st.button("←", key="back_studio"):
                        st.session_state.stage = 3
                        st.rerun()
                with gen_col:
                    if st.button("Generate 3 directions →", type="primary"):
                        try:
                            st.session_state.concepts = make_concepts(direction, st.session_state.brief)
                            st.rerun()
                        except Exception as exc:
                            api_error(exc)
        else:
            concepts = st.session_state.concepts
            st.markdown('<div class="concept-grid">', unsafe_allow_html=True)
            for index, concept in enumerate(concepts):
                st.markdown(f'''<div class="concept-card"><div class="concept-number">Concept 0{index+1}</div><div class="concept-title">{concept.get("name", "Concept")}</div><div class="concept-tagline">{concept.get("tagline", "")}</div><div class="concept-detail"><strong>Layout:</strong> {concept.get("layout", "")}<br><strong>Hero:</strong> {concept.get("hero", "")}</div></div>''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            with actions():
                cols = st.columns(4, gap="small")
                with cols[0]:
                    if st.button("←", key="back_concepts"):
                        st.session_state.concepts = None
                        st.rerun()
                for index, concept in enumerate(concepts):
                    with cols[index + 1]:
                        if st.button(f"Choose 0{index+1} →", key=f"choose_{index}", type="primary"):
                            st.session_state.selected_concept = concept
                            st.session_state.stage = 5
                            st.rerun()

# Stage 5 — text co-design
elif st.session_state.stage == 5:
    selected = (st.session_state.revision.get("updated_concept") if st.session_state.revision else st.session_state.selected_concept) or {}
    with st.container(key="screen"):
        st.markdown(f'<h1 class="question">{selected.get("name", "Selected concept")}</h1>', unsafe_allow_html=True)
        st.markdown(f'<div class="subcopy">{selected.get("tagline", "Give Coform one change at a time. It will keep what you liked and revise what you rejected.")}</div>', unsafe_allow_html=True)
        st.markdown(f'''<div class="concept-card" style="width:min(700px,100%);margin:18px auto 0"><div class="concept-number">Current direction</div><div class="concept-detail"><strong>Layout:</strong> {selected.get("layout", "")}<br><strong>Hero:</strong> {selected.get("hero", "")}<br><strong>Interaction:</strong> {selected.get("interaction", "")}</div></div>''', unsafe_allow_html=True)
        dna = st.session_state.dna or {}
        dna_html = ''.join(f'<div class="dna-item"><strong>{key}</strong><span>{" · ".join(value) if isinstance(value, list) else value}</span></div>' for key, value in dna.items())
        st.markdown(f'<div class="dna"><div class="dna-title">Design DNA</div><div class="dna-head">What Coform has learned.</div><div class="dna-grid">{dna_html}</div></div>', unsafe_allow_html=True)
        if st.session_state.revision:
            st.markdown(f'<div class="summary">{st.session_state.revision.get("summary", "Updated based on your feedback.")}</div>', unsafe_allow_html=True)
        st.markdown('<div class="feedback-box"><div class="feedback-label">Human feedback</div>', unsafe_allow_html=True)
        with st.container(key="inputbox"):
            feedback = st.text_area("Feedback", placeholder="Keep the typography, but make the composition less corporate and give imagery more presence.", height=90, label_visibility="collapsed", key="feedback_input")
        st.markdown('</div>', unsafe_allow_html=True)
        with actions():
            back_col, adapt_col = st.columns(2, gap="small")
            with back_col:
                if st.button("←", key="back_codesign"):
                    st.session_state.stage = 4
                    st.rerun()
            with adapt_col:
                if st.button("Adapt the direction →", type="primary", disabled=not feedback.strip()):
                    try:
                        revision = revise(st.session_state.direction or {}, selected, feedback.strip(), dna)
                        st.session_state.revision = revision
                        st.session_state.dna = revision.get("dna", dna)
                        st.rerun()
                    except Exception as exc:
                        api_error(exc)

st.markdown('<div class="credit">Built by <strong>Soheil Faridmanesh</strong></div>', unsafe_allow_html=True)
