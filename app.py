import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. الستايل والواجهة ---
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

# --- 2. تهيئة المفاتيح وفحص الموديل ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    
    # اختيار الموديل المتاح تلقائياً لتجنب خطأ 404
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = models[0] if models else "gemini-pro"
except Exception as e:
    st.error("⚠️ تأكدي من المفاتيح في Secrets")
    st.stop()

# --- 3. دالة تحويل النص لصوت (Direct API) ---
def get_audio(text, voice_id):
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
        # عرض الخطأ إذا كان هناك مشكلة في الرصيد أو المفتاح
        st.error(f"خطأ من سيرفر الصوت: {response.text}")
        return None

# --- 4. واجهة المستخدم ---
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
            task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:5000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة: {full_text[:5000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this as a dialogue between Sarah and Nora: {full_text[:5000]}"

        if task:
            with st.spinner("جاري تحويل السوالف لصوت... 🎧"):
                try:
                    # 1. توليد السكريبت
                    model = genai.GenerativeModel(WORKING_MODEL)
                    response = model.generate_content([
                        "أنتِ سارة ونورة. التنسيق: سارة: [نص] نورة: [نص]. 3 تبادلات فقط.",
                        task
                    ])
                    
                    # 2. تقسيم السكريبت ومعالجة الصوت
                    lines = [l for l in response.text.split('\n') if ':' in l]
                    
                    # الـ IDs هذي هي أصوات Premade (مجانية ومسموحة 100% للـ API)
                    # Rachel (سارة) و Bella (نورة)
                    SARAH_VOICE = "21m0pTQbwHOo96WRhcpx" 
                    NORA_VOICE = "EXAVITQu4vr4xnNLTSrf"

                    for line in lines:
                        name, speech = line.split(':', 1)
                        # اختيار الصوت بناءً على الاسم
                        vid = SARAH_VOICE if "سارة" in name or "Sarah" in name else NORA_VOICE
                        
                        audio_data = get_audio(speech.strip(), vid)
                        if audio_data:
                            st.audio(audio_data, format="audio/mp3")
                    
                    st.info("اسمعي السالفة بالترتيب ✨")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
