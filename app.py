import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs
import io

# --- 1. الإعدادات ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

# استدعاء المفاتيح من السيكرتس
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
except Exception:
    st.error("⚠️ تأكدي من إضافة كل المفاتيح في Secrets (GEMINI_API_KEY, ELEVENLABS_API_KEY, VOICE_ID_1, VOICE_ID_2)")
    st.stop()

# تهيئة الأدوات
genai.configure(api_key=GEMINI_KEY)
client = ElevenLabs(api_key=ELEVEN_KEY)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #8A1538; color: white; font-weight: bold; height: 3.5em; }
    h1 { color: #8A1538; text-align: center; }
    .chat-box { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #eee; background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! اضغطي لتبدأ السالفة")
        
        if st.button("🎙️ ابدئي السوالف (نجدي طبيعي)"):
            with st.spinner("سارة ونورة يجهزون القهوة وبيسولفون لك... ☕"):
                
                prompt = f"المحتوى: {full_text[:3000]}\nالمطلوب: حوار ممتع بين بنتين (سارة ونورة) بلهجة نجدية بيضاء يشرحون المحتوى.\nسارة: [النص]\nنورة: [النص]\n(اكتفي بـ 3 تبادلات فقط)."
                
                script = ""
                # قائمة بأسماء الموديلات الممكنة لتجنب خطأ 404
                model_names = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'gemini-pro']
                
                for m_name in model_names:
                    try:
                        model = genai.GenerativeModel(m_name)
                        response = model.generate_content(prompt)
                        script = response.text
                        if script: break # إذا نجح، اخرج من الحلقة
                    except Exception:
                        continue # إذا فشل، جرب الاسم اللي بعده
                
                if not script:
                    st.error("عجزنا نتصل بالذكاء الاصطناعي، تأكدي من مفتاح الـ API")
                    st.stop()

                lines = [line for line in script.strip().split('\n') if ':' in line]
                
                for line in lines:
                    try:
                        name, text = line.split(':', 1)
                        voice_id = VOICE_1 if "سارة" in name else VOICE_2
                        
                        st.markdown(f"<div class='chat-box'><b>{name}:</b> {text}</div>", unsafe_allow_html=True)
                        
                        # توليد الصوت
                        audio = client.generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
                        audio_bytes = b"".join(list(audio))
                        st.audio(audio_bytes, format="audio/mp3")
                    except Exception as e:
                        st.warning(f"مشكلة بسيطة: {e}")

    else:
        st.error("المعذرة، الملف ما فيه نص نقدر نقراه.")
