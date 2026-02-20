import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# جلب المفتاح
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_KEY)
except Exception as e:
    st.error(f"❌ مشكلة في Secrets: {e}")
    st.stop()

st.title("🌸 فحص مشكلة فزعة")

uploaded_file = st.file_uploader("ارفعي ملف PDF للفحص", type="pdf")

if uploaded_file:
    if st.button("اضغطي هنا للكشف عن الخطأ"):
        with st.spinner("جاري الاتصال بجوجل..."):
            try:
                # بنجرب نكلم الموديل ونشوف وش العلة بالضبط
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Say hello")
                st.success("✅ جماني رد علينا! المشكلة مو من الموديل.")
                st.write(response.text)
            except Exception as e:
                st.error("⚠️ هذا هو الخطأ الحقيقي:")
                st.code(str(e)) # بيعرض الكود التقني للخطأ في مربع أسود
                st.info("صوري الشاشة الحين ووريني وش مكتوب في المربع الأسود")
