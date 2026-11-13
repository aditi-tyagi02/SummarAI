import json
import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader

st.set_page_config(
    page_title="SummarAI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

load_dotenv()
MODEL = "gemini-3.5-flash"
MAX_WORDS = 50000

LENGTHS = {
    "Short": {"Paragraph": "2-3 sentences", "Bullet points": "3-4 bullet points"},
    "Medium": {"Paragraph": "one paragraph of 4-6 sentences", "Bullet points": "5-7 bullet points"},
    "Detailed": {"Paragraph": "2-3 paragraphs", "Bullet points": "8-12 bullet points"},
}
LANGUAGES = ["English", "Hindi", "Spanish", "French", "German", "Portuguese"]

# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Background: soft light-blue gradient */
    .stApp {
        background:
            radial-gradient(900px 420px at 88% -8%, #CFE1FF 0%, rgba(207,225,255,0) 70%),
            radial-gradient(700px 380px at 5% 12%, #DDEBFF 0%, rgba(221,235,255,0) 70%),
            linear-gradient(180deg, #E8F1FF 0%, #F2F7FF 45%, #FAFCFF 100%);
        background-attachment: fixed;
    }

    /* Hide Streamlit chrome, including the Deploy button */
    footer, #MainMenu { visibility: hidden; }
    header[data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stAppDeployButton"],
    .stAppDeployButton,
    [data-testid="stDecoration"],
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1080px; }

    /* Header */
    .topbar {
        background: rgba(255,255,255,0.72);
        border: 1px solid #D6E4F8;
        border-radius: 18px;
        padding: 1.1rem 1.6rem 1.5rem 1.6rem;
        box-shadow: 0 8px 30px rgba(37,99,235,0.08);
    }
    .brand { display: flex; align-items: center; gap: 10px; font-weight: 600; color: #1E293B; font-size: 0.98rem; }
    .brand-icon {
        width: 34px; height: 34px; border-radius: 10px; background: #2563EB;
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 12px rgba(37,99,235,0.35);
    }
    .topbar h1 {
        color: #14213D !important; font-size: 2.5rem; font-weight: 700;
        letter-spacing: -0.02em; margin: 1rem 0 0 0; padding: 0; line-height: 1.12;
    }
    .topbar p { color: #5B6B84; margin: 0.45rem 0 0 0; font-size: 1rem; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 1rem; }
    .chip {
        background: #EAF2FF; color: #1D4ED8; border: 1px solid #D3E3FB;
        font-size: 0.75rem; font-weight: 500; padding: 4px 12px; border-radius: 999px;
    }

    /* Cards */
    .st-key-settings_card, .st-key-input_card, .st-key-result_card {
        background: rgba(255,255,255,0.88) !important;
        border: 1px solid #D6E4F8 !important;
        border-radius: 18px !important;
        padding: 0.6rem 0.9rem 0.9rem 0.9rem;
        box-shadow: 0 8px 30px rgba(37,99,235,0.07);
    }
    .card-title { font-size: 1.1rem; font-weight: 600; color: #14213D; margin: 0.4rem 0 0 0; }
    .card-hint { font-size: 0.85rem; color: #64748B; margin: 0.15rem 0 0.9rem 0; }

    /* Settings controls */
    [data-testid="stSelectbox"] label p {
        font-size: 0.7rem; font-weight: 500; color: #64748B;
        text-transform: uppercase; letter-spacing: 0.03em;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #F1F6FE; border: 1px solid #E1EBFA; border-radius: 12px;
        min-height: 3.2rem; font-weight: 600; color: #14213D;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover { border-color: #93B4F0; }

    /* Input switcher (pill style) */
    [data-testid="stRadio"] div[role="radiogroup"] { gap: 0.5rem; }
    [data-testid="stRadio"] div[role="radiogroup"] label {
        background: #fff; border: 1px solid #D6E4F8; border-radius: 999px;
        padding: 5px 16px; cursor: pointer; transition: all 0.15s ease;
    }
    [data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 0.85rem; font-weight: 500; color: #475569;
    }
    [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: #2563EB; border-color: #2563EB;
    }
    [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p { color: #fff; }
    [data-testid="stRadio"] div[role="radiogroup"] label > div:first-child { display: none; }

    /* Text area and uploader */
    [data-testid="stTextArea"] textarea {
        background: #fff; border: 1px solid #D6E4F8; border-radius: 14px; font-size: 0.95rem;
    }
    [data-testid="stTextArea"] textarea:focus { border-color: #2563EB; box-shadow: 0 0 0 3px rgba(37,99,235,0.15); }
    [data-testid="stFileUploaderDropzone"] {
        background: #F7FAFF; border: 1.5px dashed #AFC8F2; border-radius: 14px;
    }

    /* Primary button */
    .stButton > button[kind="primary"] {
        width: 100%; background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        border: none; color: #fff; border-radius: 12px; font-weight: 600;
        padding: 0.85rem 1.3rem; font-size: 1rem;
        box-shadow: 0 8px 20px rgba(37,99,235,0.28);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px); box-shadow: 0 12px 26px rgba(37,99,235,0.35); color: #fff;
    }

    /* Summary box */
    .st-key-summary_box {
        background: #F1F6FE !important; border: 1px solid #E1EBFA !important;
        border-left: 4px solid #2563EB !important; border-radius: 14px !important;
        padding: 0.4rem 0.8rem;
    }

    /* Metrics: value on top, label underneath */
    [data-testid="stMetric"] {
        display: flex; flex-direction: column-reverse;
        background: #F1F6FE; border: 1px solid #E1EBFA; border-radius: 14px; padding: 14px 18px;
    }
    [data-testid="stMetricLabel"] p { font-size: 0.78rem; color: #64748B; }
    [data-testid="stMetricValue"] { font-size: 1.8rem; font-weight: 600; color: #14213D; }

    /* Small pill buttons (download) */
    .stDownloadButton > button {
        background: #fff; border: 1px solid #BFD3F5; border-radius: 999px;
        font-size: 0.8rem; font-weight: 500; padding: 0.3rem 1rem; color: #1D4ED8;
    }
    .stDownloadButton > button:hover { background: #EAF2FF; border-color: #2563EB; color: #1D4ED8; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="topbar">
        <div class="brand">
            <div class="brand-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff"
                     stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V5a2 2 0 0 0-3-1z"/>
                    <path d="M15 5v13a3 3 0 0 0 3-3M15 10h3a2 2 0 0 0 2-2M15 14h2"/>
                </svg>
            </div>
            SummarAI
        </div>
        <h1>AI Text Summarizer</h1>
        <p>Turn lengthy documents into clear, concise summaries.</p>
        <div class="chips">
            <span class="chip">Paste text or upload PDF</span>
            <span class="chip">6 output languages</span>
            <span class="chip">Live streaming results</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- Backend helpers ----------
@st.cache_resource
def get_client():
    return genai.Client(api_key=os.environ["GEMINI_API_KEY"])


client = get_client()


def extract_pdf_text(file):
    reader = PdfReader(file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages), len(reader.pages)


def build_prompt(text, style, length, language):
    size = LENGTHS[length][style]
    if style == "Bullet points":
        fmt = f"Summarize the text below as {size}. Start each line with '- '."
    else:
        fmt = f"Summarize the text below in {size}."
    return f"{fmt} Write the summary in {language}. Output only the summary.\n\nTEXT:\n{text}"


def stream_summary(prompt):
    for chunk in client.models.generate_content_stream(model=MODEL, contents=prompt):
        if chunk.text:
            yield chunk.text


def copy_button(text):
    safe_text = json.dumps(text).replace("</", "<\\/")
    components.html(
        f"""
        <button id="copy" style="padding:5px 16px;font-size:13px;font-weight:500;
            cursor:pointer;border-radius:999px;border:1px solid #BFD3F5;
            background:#fff;color:#1D4ED8;font-family:Inter,sans-serif;">
            Copy summary
        </button>
        <script>
        const text = {safe_text};
        const btn = document.getElementById("copy");
        btn.onclick = async () => {{
            try {{
                await navigator.clipboard.writeText(text);
            }} catch (e) {{
                const ta = document.createElement("textarea");
                ta.value = text;
                document.body.appendChild(ta);
                ta.select();
                document.execCommand("copy");
                document.body.removeChild(ta);
            }}
            btn.innerText = "Copied";
            setTimeout(() => btn.innerText = "Copy summary", 2000);
        }};
        </script>
        """,
        height=42,
    )


def show_extras(summary, original_count):
    summary_count = len(summary.split())
    reduction = max(0, round((1 - summary_count / original_count) * 100))

    c1, c2, c3 = st.columns(3)
    c1.metric("Original words", f"{original_count:,}")
    c2.metric("Summary words", f"{summary_count:,}")
    c3.metric("Reduction", f"{reduction}%")

    b1, b2, _ = st.columns([1.3, 1.3, 6])
    with b1:
        copy_button(summary)
    with b2:
        st.download_button("Download TXT", summary, file_name="summary.txt")


def card_title(title, hint=""):
    hint_html = f'<div class="card-hint">{hint}</div>' if hint else '<div style="height:0.6rem"></div>'
    st.markdown(f'<div class="card-title">{title}</div>{hint_html}', unsafe_allow_html=True)


# ---------- Summary settings ----------
st.write("")
with st.container(border=True, key="settings_card"):
    card_title("Summary settings", "Choose how the summary should look.")
    s1, s2, s3 = st.columns(3)
    style = s1.selectbox("Format", ["Paragraph", "Bullet points"], index=1)
    length = s2.selectbox("Length", ["Short", "Medium", "Detailed"], index=1)
    language = s3.selectbox("Language", LANGUAGES)

# ---------- Input ----------
with st.container(border=True, key="input_card"):
    card_title("Choose your input", "Paste your text or upload a PDF document.")
    mode = st.radio(
        "Input type", ["Paste text", "Upload PDF"],
        horizontal=True, label_visibility="collapsed",
    )

    input_text = ""
    if mode == "Paste text":
        input_text = st.text_area(
            "Text", height=220, label_visibility="collapsed",
            placeholder="Paste an article, essay or notes here...",
        )
    else:
        uploaded = st.file_uploader("PDF file", type="pdf", label_visibility="collapsed")
        if uploaded:
            try:
                input_text, num_pages = extract_pdf_text(uploaded)
                st.caption(f"{uploaded.name}  |  {num_pages} pages  |  {len(input_text.split()):,} words")
            except Exception as e:
                st.error(f"Could not read this PDF: {e}")

    generate = st.button("Generate Summary", type="primary")

# ---------- Results ----------
with st.container(border=True, key="result_card"):
    card_title("Your summary")

    if generate:
        words = input_text.split()
        if not words:
            st.warning("Paste some text or upload a PDF first.")
        elif len(words) < 30:
            st.warning("Not enough text found. Scanned PDFs are images and have no readable text.")
        else:
            if len(words) > MAX_WORDS:
                st.info(f"Text is very long, so only the first {MAX_WORDS:,} words are used.")
                words = words[:MAX_WORDS]
            prompt = build_prompt(" ".join(words), style, length, language)
            try:
                with st.container(border=True, key="summary_box"):
                    summary = st.write_stream(stream_summary(prompt))
                st.session_state["result"] = {"summary": summary, "original": len(words)}
                st.success("Summary generated.")
                show_extras(summary, len(words))
            except Exception as e:
                st.error(f"Something went wrong: {e}")

    elif "result" in st.session_state:
        saved = st.session_state["result"]
        with st.container(border=True, key="summary_box"):
            st.markdown(saved["summary"])
        show_extras(saved["summary"], saved["original"])

    else:
        with st.container(border=True, key="summary_box"):
            st.markdown("Your summary will appear here.")