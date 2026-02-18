import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from gtts import gTTS
import os

# --- إعدادات جامعة نورة ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

# --- الـ API Key الخاص بك ---
genai.configure(api_key="AIzaSyCXOdsAR9FTn649dMtObx2ui8e73bF81-k")

st.title("🌸 فزعة، تسولفها")
st.subheader("من تعقيد أكاديمي… إلى جلسة سوالف")

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    st.success("تم رفع الملف! اختاري نوع الفزعة:")
    col1, col2, col3 = st.columns(3)
    prompt = ""
    
    if col1.button("🇸🇦 سولفها بالعربي"):
        prompt = f"اشرحي النص بلهجة نجدية سوالف: {full_text}"
    if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
        prompt = f"ترجمي واشرحي النص بلهجة نجدية: {full_text}"
    if col3.button("🇬🇧 English"):
        prompt = f"Explain this simply in English: {full_text}"

    if prompt:
        with st.spinner("قاعدين نفزع لك... ✨"):
            try:
                # الاستدعاء الصحيح للمودل
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(prompt)
                
                st.markdown("### 📖 الشرح المولد")
                st.write(response.text)

                # توليد الصوت
                tts = gTTS(text=response.text, lang='ar')
                tts.save("voice.mp3")
                st.audio("voice.mp3")
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
