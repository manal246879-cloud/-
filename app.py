import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs

# --- الإعدادات ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸")

# جلب المفاتيح
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    
    # تهيئة جوجل
    genai.configure(api_key=GEMINI_KEY)
    # اختيار الموديل المستقر
    model = genai.GenerativeModel('gemini-pro')
    client = ElevenLabs(api_key=ELEVEN_KEY)
    
except Exception as e:
    st.error("❌ مشكلة في المفاتيح (Secrets)")
    st.code(str(e))
    st.stop()

st.markdown("<h1 style='text-align: center; color: #8A1538;'>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("المفتاح شغال! ✅")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي هذا المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:5000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي المحتوى بلهجة نجدية سوالف بين سارة ونورة: {full_text[:5000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this in English conversation between Sarah and Nora: {full_text[:5000]}"

        if task:
            with st.spinner("قاعدين نضبط السالفة..."):
                try:
                    response = model.generate_content([
                        "Format: Sarah: [text] Nora: [text]. Max 3 exchanges.",
                        task
                    ])
                    script = response.text
                    lines = [l.strip() for l in script.split('\n') if ':' in l]
                    
                    for line in lines:
                        name, text = line.split(':', 1)
                        vid = VOICE_1 if "سارة" in name or "Sarah" in name else VOICE_2
                        st.markdown(f"**{name}:** {text}")
                        audio = client.generate(text=text, voice=vid, model="eleven_multilingual_v2")
                        st.audio(b"".join(list(audio)), format="audio/mp3")
                except Exception as e:
                    st.error("حدث خطأ أثناء المحادثة:")
                    st.code(str(e))
