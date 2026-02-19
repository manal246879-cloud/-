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
# تأكدي من وضع مفتاحك هنا
API_KEY = "AIzaSyAg5uwFJdtDZ4GXHQ2tRzmgIU_OAHBoaOU"
genai.configure(api_key=API_KEY)

# --- 3. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>من تعقيد أكاديمي… إلى جلسة سوالف</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    # قراءة النص من الـ PDF
    try:
        reader = PdfReader(uploaded_file)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text
        
        if full_text:
            st.success("تم قراءة الملف بنجاح! اختاري نوع الفزعة:")
            
            col1, col2, col3 = st.columns(3)
            final_prompt = ""

            # تعليمات النظام الأساسية
            base_instruction = "أنتِ خبيرة أكاديمية بأسلوب سوالف نجدية. لا تلخصي، بل اشرحي بعمق وتفصيل ممل مع الحفاظ على المصطلحات العلمية. لا تستخدمي معلومات خارج النص. استخدمي إيموجيات لطيفة ✨."

            if col1.button("🇸🇦 سولفها بالعربي"):
                final_prompt = f"{base_instruction} اشرحي النص التالي بلهجة نجدية بيضاء وشرح مفصل جداً: {full_text}"
            
            if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
                final_prompt = f"{base_instruction} ترجمي واشرحي النص التالي من الإنجليزية للعربية بلهجة نجدية سوالف، مع إبقاء المصطلحات الإنجليزية بين قوسين: {full_text}"
            
            if col3.button("🇬🇧 English to English"):
                final_prompt = f"Explain this academic text in a deep-dive, friendly conversational English. Do not summarize, explain everything in detail. Text: {full_text}"

            if final_prompt:
                with st.spinner("قاعدين نفزع لك... السوالف بالطريق ✨"):
                    # استخدام gemini-1.5-flash لأنه أضمن للتشغيل السريع
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(final_prompt)
                    
                    st.markdown("---")
                    st.markdown("### 📖 الشرح المولد (سوالفنا)")
                    st.write(response.text)

                    # توليد الصوت
                    tts = gTTS(text=response.text[:1500], lang='ar') # أول 1500 حرف لضمان السرعة
                    tts.save("voice.mp3")
                    st.audio("voice.mp3")
                    
                    st.download_button("تحميل الشرح نصياً", response.text, file_name="fazaa_explanation.txt")
        else:
            st.error("لم نتمكن من استخراج نص من هذا الملف. تأكدي أنه ليس ملفاً مصوراً (Scanner).")
            
    except Exception as e:
        st.error(f"حدث خطأ أثناء المعالجة: {e}")
else:
    st.info("ارفعي الملف عشان نبدأ السوالف..")
