import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import elevenlabs

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
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    
    genai.configure(api_key=GEMINI_KEY)
    
    # تهيئة اليفن لابز بالطريقة الجديدة والقديمة سوا عشان نضمنها
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=ELEVEN_KEY)
    except:
        elevenlabs.set_api_key(ELEVEN_KEY)

except Exception as e:
    st.error("⚠️ تأكدي من إعداد Secrets بشكل صحيح.")
    st.stop()

# --- 3. اختيار الموديل تلقائياً (حل 404) ---
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if '1.5-flash' in m: return m
        return models[0] if models else "gemini-pro"
    except: return "gemini-pro"

# --- 4. الواجهة ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز!")
        col1, col2, col3 = st.columns(3)
        
        prompt_task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            prompt_task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            prompt_task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة: {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            prompt_task = f"Explain this in English dialogue between Sarah and Nora: {full_text[:6000]}"

        if prompt_task:
            with st.spinner("جاري تجهيز السوالف صوتياً... 🎧"):
                try:
                    model = genai.GenerativeModel(get_working_model())
                    response = model.generate_content([
                        "أنتِ سارة ونورة. التنسيق: سارة: [نص] نورة: [نص]. اكتفي بـ 3 تبادلات.",
                        prompt_task
                    ])
                    
                    lines = [l.strip() for l in response.text.split('\n') if ':' in l]
                    
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            vid = VOICE_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_2
                            
                            # محاولة توليد الصوت بكل الطرق الممكنة للمكتبة
                            try:
                                # الطريقة 1 (الجديدة)
                                audio_gen = client.generate(text=text.strip(), voice=vid, model="eleven_multilingual_v2")
                                audio_bytes = b"".join(list(audio_gen))
                            except:
                                # الطريقة 2 (القديمة)
                                audio_bytes = elevenlabs.generate(text=text.strip(), voice=vid, model="eleven_multilingual_v2")
                            
                            st.audio(audio_bytes, format="audio/mp3")
                        except Exception as inner_e:
                            st.error(f"خطأ في توليد الصوت: {inner_e}")
                            
                    st.info("اسمعي السالفة بالترتيب ✨")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
