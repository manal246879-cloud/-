import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. الإعدادات ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    h1 { color: #8A1538; text-align: center; font-family: 'Tajawal'; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    st.error("⚠️ تأكدي من إعداد مفاتيح API في Secrets")
    st.stop()

# --- 3. دالة تحويل النص لصوت مع كاشف أخطاء دقيق ---
def text_to_speech(text, voice_id, line_index):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        return response.content
    else:
        # إذا فشل الصوت، سنعرض الخطأ لنعرف السبب
        st.error(f"فشل تشغيل المقطع {line_index}: {response.text}")
        return None

# --- 4. الواجهة ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز!")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة: {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this in English dialogue between Sarah and Nora: {full_text[:6000]}"

        if task:
            with st.spinner("جاري تجهيز السوالف صوتياً... 🎧"):
                try:
                    # محاولة استخدام أكثر من اسم للموديل لضمان العمل
                    model_name = 'gemini-1.5-flash'
                    model = genai.GenerativeModel(model_name)
                    
                    response = model.generate_content([
                        "You are Sarah and Nora. Format: Sarah: [text] Nora: [text]. Max 3 exchanges.",
                        task
                    ])
                    
                    lines = [l.strip() for l in response.text.split('\n') if ':' in l]
                    
                    # IDs أصوات أساسية (Rachel و Bella)
                    # إذا استمر الخطأ، سنعرف من رسالة الخطأ التي ستظهر
                    V1 = "21m0pTQbwHOo96WRhcpx" 
                    V2 = "EXAVITQu4vr4xnNLTSrf"

                    audio_success = False
                    for i, line in enumerate(lines, 1):
                        name, text = line.split(':', 1)
                        current_vid = V1 if "sarah" in name.lower() or "سارة" in name else V2
                        
                        audio_data = text_to_speech(text.strip(), current_vid, i)
                        if audio_data:
                            st.audio(audio_data, format="audio/mp3")
                            audio_success = True
                    
                    if audio_success:
                        st.info("اسمعي السالفة بالترتيب ✨")
                        
                except Exception as e:
                    st.error(f"حدث خطأ في النظام: {e}")
