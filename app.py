import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from gtts import gTTS
import os
import tempfile

# إعدادات الصفحة
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

# جلب المفتاح بأمان
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات Secrets.")
    st.stop()

st.title("🌸 فزعة، تسولفها")
st.subheader("من تعقيد أكاديمي… إلى جلسة سوالف")

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        # قراءة أول 15 صفحة
        pages_to_read = reader.pages[:15] 
        text_list = [page.extract_text() for page in pages_to_read if page.extract_text()]
        full_text = " ".join(text_list)
        
        if not full_text:
            st.error("الملف غير قابل للقراءة.")
            st.stop()
            
    except Exception as e:
        st.error(f"خطأ في الملف: {e}")
        st.stop()

    st.success("تم رفع الملف! اختاري نوع الفزعة:")
    col1, col2, col3 = st.columns(3)
    prompt = ""
    
    context = f"\n\n Text: {full_text[:10000]}"

    if col1.button("🇸🇦 سولفها بالعربي"):
        prompt = "اشرحي هالمحتوى بلهجة نجدية عفوية كأنك تسولفين معي:" + context
    if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
        prompt = "ترجمي واشرحي هالمحتوى بلهجة نجدية:" + context
    if col3.button("🇬🇧 English"):
        prompt = "Explain this in simple conversational English:" + context

    if prompt:
        with st.spinner("قاعدين نفزع لك... ✨"):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                response = model.generate_content(prompt)
                
                if response.text:
                    st.markdown("### 📖 الشرح المولد")
                    st.write(response.text)

                    with st.spinner("جاري تجهيز الصوت..."):
                        lang = 'en' if "English" in prompt else 'ar'
                        tts = gTTS(text=response.text[:1000], lang=lang)
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                            tts.save(fp.name)
                            st.audio(fp.name)
                            os.unlink(fp.name)
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
