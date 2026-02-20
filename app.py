import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs
import io

# --- 1. الإعدادات ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

# استدعاء المفاتيح من السيكرتس
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
VOICE_1 = st.secrets["VOICE_ID_1"]
VOICE_2 = st.secrets["VOICE_ID_2"]

# تهيئة الأدوات
genai.configure(api_key=GEMINI_KEY)
client = ElevenLabs(api_key=ELEVEN_KEY)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 25px; background-color: #8A1538; color: white; font-weight: bold; }
    h1 { color: #8A1538; text-align: center; }
    .chat-box { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>حولي تعقيد المحاضرات.. لجلسة سوالف بين بنتين ✨</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([page.extract_text() for page in reader.pages])
    
    if full_text.strip():
        st.success("الملف جاهز! اضغطي لتبدأ السالفة")
        
        if st.button("🎙️ ابدئي السوالف (نجدي طبيعي)"):
            with st.spinner("سارة ونورة يجهزون القهوة وبيسولفون لك... ☕"):
                
                # صياغة البرومبت للحصول على حوار
                prompt = f"""
                أنتِ خبيرة في تحويل المحتوى الأكاديمي إلى حوار طبيعي جداً.
                المحتوى: {full_text[:4000]}
                المطلوب: كتابة حوار قصير وممتع بين بنتين (سارة ونورة) بلهجة نجدية بيضاء (سولفي كأنك بنت سعودية حقيقية).
                - سارة: تبدأ الكلام وتسأل أو تعطي معلومة.
                - نورة: ترد عليها وتشرح جزء بأسلوب "تخيلي.." أو "يا بنت شوفي..".
                - اجعلي الكلام بشري وانساني جداً، استخدمي كلمات مثل (يا حبيلك، تخيلي، من جد، يا بنت).
                - التنسيق يجب أن يكون:
                سارة: [النص]
                نورة: [النص]
                (اكتفي بـ 4 تبادلات فقط لضمان السرعة).
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                script = response.text
                
                # تقسيم الحوار وتوليد الصوت
                lines = script.strip().split('\n')
                for line in lines:
                    if ':' in line:
                        name, text = line.split(':', 1)
                        voice_id = VOICE_1 if "سارة" in name else VOICE_2
                        
                        st.markdown(f"<div class='chat-box'><b>{name}:</b> {text}</div>", unsafe_allow_html=True)
                        
                        # توليد الصوت من ElevenLabs
                        audio = client.generate(
                            text=text,
                            voice=voice_id,
                            model="eleven_multilingual_v2"
                        )
                        
                        # تحويل الصوت لصيغة يفهمها Streamlit
                        audio_bytes = b"".join(list(audio))
                        st.audio(audio_bytes, format="audio/mp3")

    else:
        st.error("الملف فاضي أو ما قدرنا نقراه.")
