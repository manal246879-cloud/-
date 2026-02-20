import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

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

# --- 2. تهيئة المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    st.error("⚠️ تأكدي من إعداد API Keys في Secrets (Gemini و ElevenLabs)")
    st.stop()

# --- 3. دالة لجلب الأصوات المجانية المتاحة في حسابك تلقائياً ---
def get_available_voices():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {"xi-api-key": ELEVEN_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        voices = response.json().get('voices', [])
        # تصفية الأصوات لاختيار الأصوات الأساسية (Premade) فقط لتجنب خطأ الدفع
        premade_voices = [v['voice_id'] for v in voices if v.get('category') == 'premade']
        if len(premade_voices) >= 2:
            return premade_voices[0], premade_voices[1]
        elif len(premade_voices) == 1:
            return premade_voices[0], premade_voices[0]
        else:
            # إذا لم يجد أصوات بريميد، يأخذ أول أصوات متاحة
            all_ids = [v['voice_id'] for v in voices]
            return all_ids[0], all_ids[1]
    return None, None

# --- 4. دالة تحويل النص لصوت ---
def text_to_speech_direct(text, voice_id):
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
    return None

# --- 5. اختيار موديل جماني ---
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if '1.5-flash' in m: return m
        return models[0]
    except: return "gemini-pro"

# --- 6. الواجهة ---
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
            with st.spinner("جاري تجهيز السوالف... 🎧"):
                # جلب الأصوات المسموحة تلقائياً
                v1, v2 = get_available_voices()
                if not v1:
                    st.error("لم نتمكن من العثور على أصوات متاحة في حسابك.")
                    st.stop()
                
                try:
                    model = genai.GenerativeModel(get_model())
                    response = model.generate_content([
                        "أنتِ سارة ونورة. التنسيق: سارة: [نص] نورة: [نص]. اكتفي بـ 3 تبادلات.",
                        task
                    ])
                    
                    lines = [l.strip() for l in response.text.split('\n') if ':' in l]
                    
                    for line in lines:
                        name, text = line.split(':', 1)
                        # استخدام الصوت الأول لسارة والثاني لنورة تلقائياً
                        current_vid = v1 if any(n in name.lower() for n in ["سارة", "sarah"]) else v2
                        
                        audio_data = text_to_speech_direct(text.strip(), current_vid)
                        if audio_data:
                            st.audio(audio_data, format="audio/mp3")
                            
                    st.info("اسمعي السالفة بالترتيب ✨")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
