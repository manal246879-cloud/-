import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. إعدادات الواجهة والستايل ---
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

# --- 2. تهيئة المفاتيح وفحص الموديل ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    
    # البحث عن موديل جماني المتاح تلقائياً
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = models[0] if models else "gemini-pro"
except Exception as e:
    st.error("⚠️ تأكدي من ضبط Secrets بشكل صحيح (GEMINI_API_KEY و ELEVENLABS_API_KEY)")
    st.stop()

# --- 3. دالة تحويل النص لصوت (Direct API) ---
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
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75} # جودة عالية
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"خطأ في الصوت: {response.text}")
        return None

# --- 4. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    # نأخذ أول 10 صفحات فقط لضمان عدم استهلاك الحروف بسرعة
    full_text = "".join([p.extract_text() for p in reader.pages[:10] if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! اختاري كيف تبين الشرح:")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي هذا المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة. اجعلي الحوار طويلاً ومفصلاً (حوالي 10 تبادلات): {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة بشكل مفصل (10 تبادلات): {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this content in a natural English dialogue between Sarah and Nora (10 exchanges): {full_text[:6000]}"

        if task:
            with st.spinner("جاري تجهيز السوالف صوتياً... 🎧"):
                try:
                    # 1. توليد السكريبت من Gemini
                    model = genai.GenerativeModel(WORKING_MODEL)
                    response = model.generate_content([
                        "أنتِ سارة ونورة. حولي النص لحوار سوالف بنات طبيعي جداً. التنسيق: سارة: [نص] نورة: [نص]. التزمي بـ 10 تبادلات حوارية (20 جملة إجمالاً).",
                        task
                    ])
                    
                    # 2. تقسيم الحوار ومعالجته
                    lines = [l.strip() for l in response.text.split('\n') if ':' in l]
                    
                    # أصوات Rachel و Bella (أفضل أصوات للمشتركين)
                    VOICE_SARAH = "21m0pTQbwHOo96WRhcpx" 
                    VOICE_NORA = "EXAVITQu4vr4xnNLTSrf"

                    # 3. تحويل كل جملة لصوت وعرضها
                    for i, line in enumerate(lines):
                        try:
                            name, text = line.split(':', 1)
                            # تبديل الأصوات بناءً على الاسم
                            vid = VOICE_SARAH if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_NORA
                            
                            audio_data = text_to_speech(text.strip(), vid)
                            if audio_data:
                                # عرض مشغل الصوت مع تسمية بسيطة (سارة 1، نورة 1...)
                                st.audio(audio_data, format="audio/mp3")
                        except:
                            continue
                    
                    st.info("اسمعي السالفة بالترتيب من الأعلى ✨")
                    st.caption(f"تم استهلاك حوالي {len(response.text)} حرف من باقتك.")
                    
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
