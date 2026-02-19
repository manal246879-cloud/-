import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs
import os
import tempfile

# --- 1. إعدادات الهوية ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    .stButton>button:hover { background-color: #FCE4EC !important; color: #8A1538 !important; border: 1px solid #8A1538 !important; }
    h1, h2, h3 { color: #8A1538; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- 2. API Keys ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
eleven = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# --- 3. اختيار موديل ---
def get_available_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in models:
            return 'gemini-1.5-flash'
        return models[0]
    except:
        return 'gemini-1.5-flash'

# --- 4. الواجهة ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>من تعقيد أكاديمي… إلى جلسة سوالف صوتية</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = ""

    for page in reader.pages:
        t = page.extract_text()
        if t:
            full_text += t

    if full_text:
        st.success("تم رفع الملف! اختاري الفزعة المطلوبة:")

        if st.button("🎙️ خلهم يسولفون Deep Dive"):
            
            with st.spinner("قاعدين يسولفون لك ✨"):
                
                model_name = get_available_model()
                model = genai.GenerativeModel(model_name)

                prompt = f"""
                حوّل النص التالي إلى جلسة سوالف بين بنت وولد بأسلوب Deep Dive،
                سوالف نجدية بيضاء طبيعية جدًا،
                يخوضون في التفاصيل الأكاديمية لكن بأسلوب ممتع،
                لا تكتب مقدمات رسمية.

                النص:
                {full_text[:15000]}
                """

                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.8,
                        "max_output_tokens": 3000
                    }
                )

                conversation_text = response.text

                # --- تقسيم النص بين صوتين ---
                lines = conversation_text.split("\n")
                
                audio_segments = []

                for i, line in enumerate(lines):
                    if not line.strip():
                        continue
                    
                    # بالتناوب: بنت ثم ولد
                    voice_id = "Rachel" if i % 2 == 0 else "Josh"

                    audio = eleven.text_to_speech.convert(
                        voice_id=voice_id,
                        model_id="eleven_multilingual_v2",
                        text=line
                    )

                    aud
