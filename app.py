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
    }
    .stButton>button:hover { background-color: #FCE4EC !important; color: #8A1538 !important; border: 1px solid #8A1538 !important; }
    h1, h2, h3 { color: #8A1538; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد الـ API ---
# يفضل دائماً إخفاء المفتاح، لكن سنضعه هنا للتجربة
API_KEY = "AIzaSyAg5uwFJdtDZ4GXHQ2tRzmgIU_OAHBoaOU" 
genai.configure(api_key=API_KEY)

# دالة لاختيار أفضل موديل متاح في حسابك
def get_available_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if 'models/gemini-1.5-flash' in models:
            return 'gemini-1.5-flash'
        elif 'models/gemini-1.5-pro' in models:
            return 'gemini-1.5-pro'
        elif 'models/gemini-pro' in models:
            return 'gemini-pro'
        return models[0] if models else None
    except:
        return 'gemini-1.5-flash' # fallback

# --- 3. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>من تعقيد أكاديمي… إلى جلسة سوالف</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: full_text += t
        
        if full_text:
            st.success("تم رفع الملف! اختاري الفزعة المطلوبة:")
            col1, col2, col3 = st.columns(3)
            final_prompt = ""

            base_instruction = "أنتِ خبيرة أكاديمية بأسلوب سوالف نجدية. اشرحي بعمق وتفصيل من النص فقط. استخدمي إيموجيات لطيفة ✨."

            if col1.button("🇸🇦 سولفها بالعربي"):
                final_prompt = f"{base_instruction} اشرحي هذا النص بلهجة نجدية بيضاء وشرح مفصل جداً: {full_text}"
            if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
                final_prompt = f"{base_instruction} ترجمي واشرحي هذا النص للعربي بلهجة نجدية سوالف مع إبقاء المصطلحات الإنجليزية: {full_text}"
            if col3.button("🇬🇧 English"):
                final_prompt = f"Explain this academic text in a deep-dive, friendly conversational English: {full_text}"

            if final_prompt:
                with st.spinner("قاعدين نفزع لك... ✨"):
                    model_name = get_available_model()
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(final_prompt)
                    
                    st.markdown("---")
                    st.markdown(f"### 📖 الشرح المولد (بواسطة {model_name})")
                    st.write(response.text)

                    # الصوت
                    tts = gTTS(text=response.text[:1000], lang='ar')
                    tts.save("voice.mp3")
                    st.audio("voice.mp3")
        else:
            st.error("الملف فارغ أو لا يمكن قراءته.")
    except Exception as e:
        st.error(f"حدث خطأ: {e}")
