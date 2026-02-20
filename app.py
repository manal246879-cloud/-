import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs
import io

# --- 1. إعدادات الهوية البصرية (نفس ستايلك الأصلي) ---
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

# --- 2. إعداد الـ API بشكل آمن ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    genai.configure(api_key=GEMINI_KEY)
    client = ElevenLabs(api_key=ELEVEN_KEY)
except Exception:
    st.error("⚠️ تأكدي من إضافة المفاتيح في Secrets (GEMINI_API_KEY, ELEVENLABS_API_KEY, VOICE_ID_1, VOICE_ID_2)")
    st.stop()

# --- 3. واجهة المستخدم (كلامك الأصلي) ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>حولي تعقيد المحاضرات.. لجلسة سوالف ممتعة ✨</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! وش تبين نسوي؟")
        col1, col2, col3 = st.columns(3)
        final_prompt = ""
        
        # الأزرار الأصلية مع المهام الخاصة بها
        if col1.button("🇸🇦 سولفها بالعربي"):
            final_prompt = f"اشرحي هذا المحتوى بلهجة نجدية سوالف ممتعة بين بنتين (سارة ونورة): {full_text[:3000]}"
        
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            final_prompt = f"النص بالإنجليزية، ترجميه واشرحيه بلهجة نجدية سوالف بين بنتين (سارة ونورة) مع الحفاظ على المصطلحات التقنية: {full_text[:3000]}"
        
        if col3.button("🇬🇧 English"):
            final_prompt = f"Explain this academic text in a deep-dive conversational English between two girls (Sarah and Nora): {full_text[:3000]}"

        if final_prompt:
            with st.spinner("قاعدين نضبط لك السالفة... ☕"):
                # نظام الحوار البشري
                system_instruction = "أنتِ خبيرة في تحويل المحتوى الأكاديمي إلى حوار طبيعي جداً بين بنتين (سارة ونورة). استخدمي أسلوب سوالف بنات حقيقي. التنسيق: سارة: [النص] نورة: [النص]. اكتفي بـ 3 تبادلات."
                
                script = ""
                # حل مشكلة الـ 404 بالتجربة المتكررة
                for m_name in ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro']:
                    try:
                        model = genai.GenerativeModel(m_name)
                        response = model.generate_content(f"{system_instruction}\n\n{final_prompt}")
                        script = response.text
                        if script: break
                    except: continue
                
                if script:
                    lines = [line for line in script.strip().split('\n') if ':' in line]
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            voice_id = VOICE_1 if "سارة" in name else VOICE_2
                            st.markdown(f"<div class='chat-box'><b>{name}:</b> {text}</div>", unsafe_allow_html=True)
                            
                            # توليد الصوت الطبيعي من ElevenLabs
                            audio = client.generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
                            st.audio(b"".join(list(audio)), format="audio/mp3")
                        except: continue
                    st.info("اضغطي على زر التشغيل أعلاه لسماع الشرح ✨")
    else:
        st.error("المعذرة، الملف ما فيه نص نقدر نقراه.")
