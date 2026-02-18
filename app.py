import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from gtts import gTTS
import os

# --- إعدادات الهوية البصرية (ستايل جامعة نورة) ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 25px; height: 3em; background-color: #8A1538; color: white; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #FCE4EC; color: #8A1538; border: 1px solid #8A1538; }
    h1 { color: #8A1538; }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- إعدادات API ---
# استخدمت مفتاحك المذكور في المحادثة السابقة لضمان التشغيل
genai.configure(api_key="AIzaSyCXOdsAR9FTn649dMtObx2ui8e73bF81-k")

st.image("https://upload.wikimedia.org/wikipedia/ar/thumb/0/00/PNU_Logo.svg/1200px-PNU_Logo.svg.png", width=100)
st.title("🌸 فزعة، تسولفها")
st.subheader("من تعقيد أكاديمي… إلى جلسة سوالف")

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text
    
    st.success("تم رفع الملف بنجاح! اختاري نوع الفزعة:")

    col1, col2, col3 = st.columns(3)
    prompt = ""
    lang_code = 'ar'

    with col1:
        if st.button("🇸🇦 سولفها بالعربي"):
            prompt = f"أنت فزعة، مساعدة أكاديمية. اشرحي هذا النص بلهجة نجدية بيضاء (سوالف) وبشكل مفصل جداً: {full_text}"
            lang_code = 'ar'
    with col2:
        if st.button("🇺🇸➡️🇸🇦 عربناها لك"):
            prompt = f"أنت فزعة. ترجمي واشرحي هذا النص الإنجليزي بلهجة نجدية سوالف: {full_text}"
            lang_code = 'ar'
    with col3:
        if st.button("🇬🇧 English to English"):
            prompt = f"Simplify this academic text into friendly conversational English: {full_text}"
            lang_code = 'en'

    if prompt:
        with st.spinner("جاري تحويل المحتوى إلى سوالف وتوليد الصوت... ✨"):
            try:
                # هذا السطر هو اللي كان يسبب المشكلة (تم تصحيحه)
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                result_text = response.text
                
                st.markdown("---")
                st.markdown("### 📖 الشرح المولد")
                st.write(result_text)

                # توليد الصوت الحقيقي (TTS)
                tts = gTTS(text=result_text, lang=lang_code)
                audio_path = "faza_voice.mp3"
                tts.save(audio_path)
                st.audio(audio_path)

            except Exception as e:
                st.error(f"حدث خطأ: {e}")
else:
    st.info("بانتظار ملفك الأكاديمي لنبدأ السوالف..")
