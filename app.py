import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs
import io

# --- 1. إعدادات الهوية البصرية ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #FCE4EC !important; color: #8A1538 !important; border: 1px solid #8A1538 !important; }
    h1, h2, h3 { color: #8A1538; text-align: center; }
    .chat-box { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #eee; background-color: #f9f9f9; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. التحقق من المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    genai.configure(api_key=GEMINI_KEY)
    client = ElevenLabs(api_key=ELEVEN_KEY)
except Exception as e:
    st.error(f"⚠️ نقص في إعدادات Secrets: {e}")
    st.stop()

# --- 3. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>حولي تعقيد المحاضرات.. لجلسة سوالف ممتعة ✨</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! وش تبين نسوي؟")
        col1, col2, col3 = st.columns(3)
        
        # استخدام Session State لضمان تنفيذ الأوامر عند الضغط
        action = None
        if col1.button("🇸🇦 سولفها بالعربي"): action = "ar"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"): action = "trans"
        if col3.button("🇬🇧 English"): action = "en"

        if action:
            with st.spinner("قاعدين نضبط لك السالفة... ☕"):
                # تحديد البرومبت بناءً على الزر
                if action == "ar":
                    prompt = f"اشرحي هذا المحتوى بلهجة نجدية سوالف ممتعة بين بنتين (سارة ونورة): {full_text[:3000]}"
                elif action == "trans":
                    prompt = f"النص بالإنجليزية، ترجميه واشرحيه بلهجة نجدية سوالف بين بنتين (سارة ونورة) مع الحفاظ على المصطلحات التقنية: {full_text[:3000]}"
                else:
                    prompt = f"Explain this academic text in a deep-dive conversational English between two girls (Sarah and Nora): {full_text[:3000]}"

                system_instruction = "أنتِ خبيرة في تحويل المحتوى الأكاديمي إلى حوار طبيعي جداً بين بنتين (سارة ونورة). استخدمي أسلوب سوالف بنات حقيقي. التنسيق الإلزامي: \nسارة: [نص]\nنورة: [نص]\nاكتفي بـ 3 تبادلات."

                # محاولة طلب المحتوى مع معالجة الأخطاء
                script = ""
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(f"{system_instruction}\n\n{prompt}")
                    script = response.text
                except Exception as e:
                    st.error(f"خطأ في Gemini: {e}")
                
                if script:
                    lines = [line for line in script.strip().split('\n') if ':' in line]
                    if not lines:
                        st.warning("الذكاء الاصطناعي ما عطانا حوار مرتب، جربي تضغطين الزر مرة ثانية.")
                        st.write(script) # لعرض الرد إذا فشل التقسيم
                    
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            voice_id = VOICE_1 if "سارة" in name or "Sarah" in name else VOICE_2
                            st.markdown(f"<div class='chat-box'><b>{name}:</b> {text}</div>", unsafe_allow_html=True)
                            
                            # توليد الصوت
                            audio = client.generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
                            st.audio(b"".join(list(audio)), format="audio/mp3")
                        except Exception as e:
                            st.error(f"خطأ في الصوت ({name}): {e}")
                    st.info("اضغطي على زر التشغيل أعلاه لسماع الشرح ✨")
    else:
        st.error("المعذرة، الملف ما فيه نص نقدر نقراه.")
