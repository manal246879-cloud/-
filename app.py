import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. إعدادات الصفحة والستايل ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")
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

# --- 2. تهيئة المفاتيح وفحص الموديل المتاح ---
try:
    # جلب المفاتيح من Secrets
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    
    # اختيار موديل جماني المتاح تلقائياً لتجنب خطأ 404
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = available_models[0] if available_models else "gemini-pro"
except Exception as e:
    st.error("⚠️ تأكدي من ضبط GEMINI_API_KEY و ELEVENLABS_API_KEY في Secrets")
    st.stop()

# --- 3. المعرفات التي اخترتيها (بدون أي تأليف) ---
VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 4. دالة تحويل النص لصوت (Direct API) ---
def text_to_speech(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.8}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"خطأ في الصوت: {response.text}")
        return None

# --- 5. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    # نأخذ أول 5 صفحات للاقتصاد في الحروف
    full_text = "".join([p.extract_text() for p in reader.pages[:5] if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! اختاري نوع السالفة:")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة (10 تبادلات): {full_text[:5000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة (10 تبادلات): {full_text[:5000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this as a dialogue between Sarah and Nora (10 exchanges): {full_text[:5000]}"

        if task:
            with st.spinner("جاري تجهيز السوالف... 🎧"):
                try:
                    # توليد السكريبت (20 جملة إجمالاً)
                    model = genai.GenerativeModel(WORKING_MODEL)
                    response = model.generate_content([
                        "أنتِ سارة ونورة. التنسيق: سارة: [نص] نورة: [نص]. التزمي بـ 10 تبادلات (20 جملة).",
                        task
                    ])
                    
                    lines = [l.strip() for l in response.text.split('\n') if ':' in l]

                    # تحويل كل جملة لصوت باستخدام المعرفات التي اخترتيها
                    for line in lines:
                        try:
                            name, speech = line.split(':', 1)
                            # اختيار الصوت بناءً على الاسم
                            vid = VOICE_ID_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_ID_2
                            
                            audio_data = text_to_speech(speech.strip(), vid)
                            if audio_data:
                                st.audio(audio_data, format="audio/mp3")
                        except:
                            continue
                    
                    st.info("اسمعي السالفة بالترتيب ✨")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
