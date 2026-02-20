import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. الواجهة الأصلية ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    h1 { color: #8A1538; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. التهيئة ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = next((m for m in available_models if "1.5-flash" in m), available_models[0])
except Exception as e:
    st.error(f"⚠️ خطأ: {e}")
    st.stop()

VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة الصوت (إعدادات "النبرة المتغيرة") ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # أفضل للنبرة السعودية من التربو
        "voice_settings": {
            "stability": 0.25,      # منخفض جداً عشان الصوت "يفصل" ويتحمس
            "similarity_boost": 0.75, 
            "style": 1.0,           # أعلى درجات التعبير
            "use_speaker_boost": True
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.content if response.status_code == 200 else None

# --- 4. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if file:
    reader = PdfReader(file)
    full_text = "".join([p.extract_text() for p in reader.pages[:10] if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز!")
        col1, col2, col3 = st.columns(3)
        
        task_prompt = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task_prompt = "سوالف بنات نجدية 'تمونون على بعض'. اشرحي بأسلوب ديب دايف بس بجمل قصيرة جداً ومقاطعات. استخدمي: (يووه، تخيلي، من جد، طيب، اسمعي، اممم، لحظة)."
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task
