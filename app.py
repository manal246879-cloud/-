import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from gtts import gTTS
import os

# --- 1. إعدادات الهوية البصرية (ستايل جامعة نورة) ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 20px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    .stButton>button:hover { background-color: #FCE4EC; color: #8A1538; border: 1px solid #8A1538; }
    .stHeader { color: #8A1538; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعدادات الـ API (تنبيه: لا تشاركي المفتاح مع أحد) ---
# ضعي مفتاحك هنا أو استخدمي st.secrets للأمان
os.environ["GEMINI_API_KEY"] = "AIzaSyAg5uwFJdtDZ4GXHQ2tRzmgIU_OAHBoaOU"
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# --- 3. واجهة المستخدم ---
st.markdown("<h1 style='text-align: center; color: #8A1538;'>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>من تعقيد أكاديمي… إلى جلسة سوالف ممتعة</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    # استخراج النص
    reader = PdfReader(uploaded_file)
    full_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    st.info("تم قراءة الملف بنجاح. اختاري نوع الفزعة:")
    
    col1, col2, col3 = st.columns(3)
    prompt = ""
    
    # تحسين الأوامر (Prompts) لتكون "Deep Dive"
    system_instruction = "أنتِ أكاديمية سعودية خبيرة، تشرحين بأسلوب 'سوالف' ممتع وعميق. لا تلخصين، بل تعمقي في كل مفهوم. التزمي فقط بالمعلومات الموجودة في الملف. استخدمي إيموجيات لطيفة ✨🌸."

    if col1.button("🇸🇦 سولفها بالعربي"):
        prompt = f"{system_instruction} اشرحي المحتوى التالي بلهجة نجدية بيضاء ممتعة وشرح مفصل جداً: {full_text}"
        
    if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
        prompt = f"{system_instruction} ترجمي المحتوى التالي من الإنجليزية للعربية، واشرحيه بلهجة نجدية سوالف مع الحفاظ على المصطلحات الإنجليزية المهمة بين قوسين: {full_text}"
        
    if col3.button("🇬🇧 English to English"):
        prompt = f"Explain this academic text in a deep-dive, friendly, conversational English style. Keep it intellectually rich and detailed. Use only the provided text: {full_text}"

    if prompt:
        with st.spinner("قاعدين نفزع لك ونجهز السوالف... ✨"):
            try:
                # استخدام Gemini 1.5 Pro للتحليل العميق
                model = genai.GenerativeModel('gemini-1.5-pro')
                response = model.generate_content(prompt)
                
                # عرض النتيجة
                st.markdown("---")
                st.markdown("<h3 style='color: #8A1538;'>📖 الشرح المفصل (سوالفنا)</h3>", unsafe_allow_html=True)
                st.write(response.text)

                # 4. توليد الصوت (باستخدام gTTS حالياً)
                # ملاحظة: gTTS صوته آلي، لاحقاً يمكنك الترقية لـ ElevenLabs لصوت سعودي حقيقي
                tts = gTTS(text=response.text[:1000], lang='ar') # حددنا أول 1000 حرف للتجربة
                tts.save("voice.mp3")
                st.audio("voice.mp3")
                
                st.download_button("تحميل الشرح (Text)", response.text, file_name="explanation.txt")
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {e}")
else:
    st.write("بانتظار ملفك الأكاديمي لنبدأ السوالف..")
