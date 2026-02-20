import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from gtts import gTTS
import os

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
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد الـ API بالمفتاح الجديد ---
GEMINI_API_KEY = "AIzaSyBTOVaLSFepUSl8YUlT42MneLVRWl3ZTX0"
genai.configure(api_key=GEMINI_API_KEY)

def get_available_model():
    # نستخدم 1.5-flash لأنه الأسرع والأفضل حالياً للتعامل مع النصوص المستخرجة
    return 'gemini-1.5-flash'

# --- 3. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>حولي تعقيد المحاضرات.. لجلسة سوالف ممتعة ✨</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: full_text += t + "\n"
        
        if full_text.strip():
            st.success("الملف جاهز! وش تبين نسوي؟")
            col1, col2, col3 = st.columns(3)
            final_prompt = ""

            # الشخصية النجدية الودودة
            system_behavior = "أنتِ خبيرة أكاديمية بأسلوب 'سوالف نجدية' بيضاء ولطيفة. اشرحي بعمق وتبسيط مستخدمة الإيموجيات ✨."

            if col1.button("🇸🇦 سولفها بالعربي"):
                final_prompt = f"{system_behavior} اشرحي هذا المحتوى بلهجة نجدية سوالف وشرح مفصل جداً: {full_text}"
            
            if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
                final_prompt = f"{system_behavior} النص بالإنجليزية، ترجميه واشرحيه بلهجة نجدية سوالف مع الحفاظ على المصطلحات التقنية الإنجليزية: {full_text}"
            
            if col3.button("🇬🇧 English"):
                final_prompt = f"Explain this academic text in a deep-dive, friendly conversational English: {full_text}"

            if final_prompt:
                with st.spinner("قاعدين نضبط لك الفزعة... ☕"):
                    model = genai.GenerativeModel(get_available_model())
                    response = model.generate_content(final_prompt)
                    
                    st.markdown("---")
                    st.markdown("### 📖 الشرح والزبدة:")
                    st.write(response.text)

                    # تحويل النص لصوت (لأول 800 حرف لضمان السرعة)
                    try:
                        clean_text = response.text.replace("*", "").replace("#", "")
                        tts = gTTS(text=clean_text[:800], lang='ar')
                        tts.save("voice.mp3")
                        st.audio("voice.mp3")
                    except:
                        st.info("تم توليد الشرح النصي بنجاح (الصوت غير متاح حالياً لهذه الاستجابة).")
        else:
            st.error("المعذرة، الملف ما فيه نص نقدر نقراه.")
    except Exception as e:
        st.error(f"حصل خطأ بسيط: {e}")
