import streamlit as st

_CSS = """
<style>
/* === GOOGLE FONTS === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* === DESIGN TOKENS === */
:root {
    --c-primary:      #92400e;
    --c-primary-dark: #78350f;
    --c-primary-light:#b45309;
    --c-bg:           #f9f8f4;
    --c-secondary-bg: #eae8dd;
    --c-sidebar-bg:   #e0ddd4;
    --c-text:         #2e2b23;
    --c-muted:        #6b6660;
    --c-border:       #d4cfc5;
    --shadow-card:    0 1px 4px rgba(46,43,35,.08), 0 4px 16px rgba(46,43,35,.04);
    --r-sm: 6px; --r-md: 10px; --r-lg: 16px;
}

/* === BASE === */
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif !important;
    background-color: var(--c-bg);
    color: var(--c-text);
}

/* === APP HEADER === */
h1 {
    background: linear-gradient(135deg, var(--c-primary), var(--c-primary-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700 !important;
    font-size: 2rem !important;
    letter-spacing: -0.02em;
    margin-bottom: 0.15rem !important;
}
h2 { font-weight: 600; color: var(--c-text); }
h3 { font-weight: 600; color: var(--c-text); }

/* === SIDEBAR === */
[data-testid="stSidebar"] {
    background-color: var(--c-sidebar-bg) !important;
    border-right: 1px solid var(--c-border);
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] .stSubheader {
    color: var(--c-primary) !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.5rem !important;
}
[data-testid="stSidebar"] .stMarkdown p {
    font-size: 0.875rem;
    color: var(--c-muted);
}

/* === CHAT MESSAGES === */
[data-testid="stChatMessage"] {
    border-radius: var(--r-md);
    padding: 0.875rem 1.125rem;
    margin-bottom: 0.625rem;
    border: 1px solid transparent;
    transition: border-color 0.15s ease;
}
/* Assistant bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #ffffff;
    border-left: 3px solid var(--c-primary);
    box-shadow: var(--shadow-card);
}
/* User bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: var(--c-secondary-bg);
    border-color: var(--c-border);
}

/* === METRIC CARDS === */
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid var(--c-border);
    border-radius: var(--r-md);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow-card);
    transition: transform 0.15s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px); }
[data-testid="stMetricValue"] {
    color: var(--c-primary) !important;
    font-weight: 700 !important;
}
[data-testid="stMetricDelta"] { font-weight: 500; }

/* === BUTTONS === */
.stButton > button {
    border-radius: var(--r-sm) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
    border: 1.5px solid transparent !important;
}
/* Primary / full-width buttons */
.stButton > button[kind="primary"],
.stButton > button:not([kind="secondary"]) {
    background-color: var(--c-primary) !important;
    color: #ffffff !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button:not([kind="secondary"]):hover {
    background-color: var(--c-primary-dark) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(146,64,14,.28) !important;
}
/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background-color: transparent !important;
    color: var(--c-primary) !important;
    border-color: var(--c-primary) !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: rgba(146,64,14,.06) !important;
}

/* === EXPANDERS (supplier cards, sample sections) === */
[data-testid="stExpander"] {
    border: 1px solid var(--c-border) !important;
    border-radius: var(--r-md) !important;
    margin-bottom: 0.5rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
    background: #ffffff;
}
[data-testid="stExpander"]:hover {
    border-color: var(--c-primary) !important;
    box-shadow: var(--shadow-card);
}
[data-testid="stExpander"] summary {
    font-weight: 500;
    color: var(--c-text);
}

/* === CHAT INPUT === */
[data-testid="stChatInput"] textarea {
    border-radius: var(--r-md) !important;
    border: 1.5px solid var(--c-border) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9375rem !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    background: #ffffff !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--c-primary) !important;
    box-shadow: 0 0 0 3px rgba(146,64,14,.12) !important;
}

/* === FILE UPLOADER === */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--c-border) !important;
    border-radius: var(--r-md) !important;
    transition: border-color 0.15s ease !important;
    background: rgba(249,248,244,.6) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--c-primary) !important;
}

/* === SELECT / TEXT INPUTS === */
[data-testid="stSelectbox"] > div,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stTextArea"] textarea {
    border-radius: var(--r-sm) !important;
    border-color: var(--c-border) !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--c-primary) !important;
    box-shadow: 0 0 0 3px rgba(146,64,14,.10) !important;
}

/* === STATUS BANNERS === */
[data-testid="stAlert"] {
    border-radius: var(--r-md) !important;
    border: none !important;
    border-left: 4px solid !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
}

/* === FORMS === */
[data-testid="stForm"] {
    border: 1px solid var(--c-border);
    border-radius: var(--r-lg);
    padding: 1.25rem;
    background: #ffffff;
    box-shadow: var(--shadow-card);
}

/* === PLOTLY CHARTS — subtle container === */
[data-testid="stPlotlyChart"] {
    border-radius: var(--r-md);
    overflow: hidden;
    border: 1px solid var(--c-border);
    background: #ffffff;
    box-shadow: var(--shadow-card);
}

/* === DIVIDER === */
hr {
    border-color: var(--c-border) !important;
    margin: 1.25rem 0 !important;
}

/* === MULTISELECT TAGS === */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
    background-color: rgba(146,64,14,.12) !important;
    color: var(--c-primary) !important;
    border-radius: 4px !important;
    font-weight: 500 !important;
}

/* === DOWNLOAD BUTTON === */
[data-testid="stDownloadButton"] button {
    border-radius: var(--r-sm) !important;
    font-weight: 500 !important;
    background-color: var(--c-secondary-bg) !important;
    color: var(--c-text) !important;
    border: 1px solid var(--c-border) !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: var(--c-primary) !important;
    color: var(--c-primary) !important;
}

/* === HIDE STREAMLIT CHROME === */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
