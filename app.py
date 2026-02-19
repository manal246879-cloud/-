import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs
import os
import tempfile

# ---------------------------
# 1) إعداد الصفحة
# ---------------------------
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    .stButton>button:hover { 
        background-color: #FCE4EC !important; 
        color: #8A1538 !important; 
        border: 1px solid #8A1538 !important; 
    }
    h1, h2, h3 { color: #8A1538; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# 2) التأكد من API Keys
# ---------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not GOOGLE_API_KEY:
    st.error("❌ GOOGLE_API_KEY غير موجود في Secrets")
    st.stop()

if not ELEVEN_API_KEY:
    st.error("❌ ELEVENLABS_API_KEY غير موجود في Secrets")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
eleven = ElevenLabs(api_key=ELEVEN_API_KEY)

# ---------------------------
# 3
