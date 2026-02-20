import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs

# --- 1. الهوية البصرية ---
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
    .chat-box { padding: 15px; border-radius: 15px; margin-bottom: 10px; border: 1px solid #eee; background-color: #f9f9f9; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    genai.configure(api_key=GEMINI_KEY)
    client = ElevenLabs(api_key=ELEVEN_KEY)
except Exception as e:
    st.error(f"⚠️ تأكدي من إعداد Secrets بشكل صحيح: {e}")
    st.stop()

# --- 3. الواجهة ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>حولي تعقيد المحاضرات.. لجلسة سوالف ممتعة ✨</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! وش تبين نسوي؟")
        col1, col2, col3 = st.columns(3)
        
        final_prompt = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            final_prompt = f"اشرحي المحتوى التالي بلهجة نجدية سوالف بنات عفوية وممتعة جداً بين (سارة ونورة): {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            final_prompt = f"النص التالي بالإنجليزية، ترجميه واشرحيه بلهجة نجدية سوالف بين بنتين (سارة ونورة) مع تبسيط المصطلحات: {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            final_prompt = f"Explain this academic text in a friendly conversational English dialogue between two girls (Sarah and Nora): {full_text[:6000]}"

        if final_prompt:
            with st.spinner("سارة ونورة يجهزون القهوة وبيسولفون لك... ☕"):
                sys_msg = "You are an expert at turning academic text into natural conversations between two girls, Sarah and Nora. Use a very casual tone. Format: Sarah: [text] Nora: [text]. Max 3 exchanges."
                
                script = ""
                # الحل النهائي: تجربة الموديلات المستقرة فقط
                for m_name in ['gemini-pro', 'gemini-1.0-pro']:
                    try:
                        model = genai.GenerativeModel(m_name)
                        response = model.generate_content([sys_msg, final_prompt])
                        script = response.text
                        if script: break
                    except: continue
                
                if not script:
                    st.error("عجزنا نوصل للذكاء الاصطناعي، تأكدي من صلاحية مفتاح الـ API الخاص بجوجل.")
                else:
                    # تقسيم النص وتحويله لصوت
                    lines = [l.strip() for l in script.split('\n') if ':' in l]
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            # اختيار الصوت بناءً على الاسم
                            vid = VOICE_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_2
                            
                            st.markdown(f"<div class='chat-box'><b>{name.strip()}:</b> {text.strip()}</div>", unsafe_allow_html=True)
                            
                            # توليد الصوت من ElevenLabs
                            audio = client.generate(text=text.strip(), voice=vid, model="eleven_multilingual_v2")
                            st.audio(b"".join(list(audio)), format="audio/mp3")
                        except: continue
                    st.info("اسمعي السالفة من أزرار التشغيل أعلاه ✨")
    else:
        st.error("المعذرة، الملف ما فيه نص نقدر نقراه.")
