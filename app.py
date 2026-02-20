import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs import generate, set_api_key

# --- 1. الستايل ---
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

# --- 2. تهيئة المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
    
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    set_api_key(ELEVEN_KEY) # تثبيت المفتاح بالطريقة المستقرة
    
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
except Exception as e:
    st.error(f"❌ مشكلة في إعدادات المفاتيح: {e}")
    st.stop()

# --- 3. دالة جلب السكريبت ---
def get_script(prompt):
    working_model = available_models[0] if available_models else "gemini-pro"
    try:
        model = genai.GenerativeModel(working_model)
        response = model.generate_content([
            "أنتِ سارة ونورة. حولي النص لحوار سوالف بنات طبيعي. التنسيق: سارة: [نص] نورة: [نص]. اكتفي بـ 3 تبادلات.",
            prompt
        ])
        return response.text
    except: return None

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
            with st.spinner("جاري تحويل السوالف لصوت... 🎧"):
                script = get_script(task)
                if script:
                    lines = [l.strip() for l in script.split('\n') if ':' in l]
                    
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            # اختيار الصوت
                            vid = VOICE_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_2
                            
                            # توليد الصوت بالطريقة المستقرة
                            audio = generate(
                                text=text.strip(),
                                voice=vid,
                                model="eleven_multilingual_v2"
                            )
                            st.audio(audio, format="audio/mp3")
                                
                        except Exception as audio_err:
                            st.error(f"❌ خطأ في الصوت: {audio_err}")
                    
                    st.info("اسمعي السالفة بالترتيب من الأعلى ✨")
                else:
                    st.error("❌ فشل في الاتصال بجوجل.")
