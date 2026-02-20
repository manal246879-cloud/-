import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import edge_tts
import asyncio
import os

# --- 1. إعدادات الهوية البصرية (جامعة نورة) ---
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
    .stAudio { margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد الـ API ---
API_KEY = "AIzaSyAB-c1_jgZ_yBoPLYAvttwx4W1DyjaVmVM" 
genai.configure(api_key=API_KEY)

# دالة لتوليد الصوت الطبيعي
async def generate_natural_audio(text, output_file):
    # نستخدم صوت "Zariyah" وهو صوت سعودي نسائي طبيعي جداً
    voice = "ar-SA-ZariyahNeural"
    communicate = edge_tts.Communicate(text, voice, rate="+10%") # تسريع بسيط ليكون حيوي أكثر
    await communicate.save(output_file)

# --- 3. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>اسمعي شرح محاضرتك كأنها سوالف بين نورة ومنال</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text:
        st.success("تم رفع الملف! اختاري وش تبين تسمعين:")
        col1, col2, col3 = st.columns(3)
        
        # سكريبت الحوار بين نورة ومنال
        base_prompt = f"""
        حولي النص الأكاديمي التالي إلى حوار "سكريبت" طويل ومفصل بين بنتين سعوديتين (نورة ومنال).
        - نورة: هي الدافورة اللي تشرح بذكاء وحماس.
        - منال: هي اللي تسأل أسئلة ذكية وتبي تفهم التفاصيل.
        - الأسلوب: سوالف نجدية عميقة، ممتعة، وبدون اختصار. 
        - اشرحي كل شيء في النص.
        - لا تكتبي (نورة:) و (منال:) في النص، اجعليه حواراً متصلاً كأنه جلسة تسجيل.
        النص: {full_text}
        """

        final_prompt = ""
        if col1.button("🇸🇦 سوالف نجدية"):
            final_prompt = base_prompt
        if col2.button("🇺🇸➡️🇸🇦 ترجمة وسوالف"):
            final_prompt = "ترجمي النص التالي للعربي ثم " + base_prompt
        if col3.button("🇬🇧 English Session"):
            final_prompt = f"Create a deep-dive conversation between two students, Nora and Manal, discussing this PDF in a friendly English style. Text: {full_text}"

        if final_prompt:
            with st.spinner("نورة ومنال قاعدين يجهزون السوالف... لحظات ✨"):
                try:
                    # 1. توليد الحوار من Gemini
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(final_prompt)
                    generated_script = response.text

                    # 2. تحويل الحوار لصوت طبيعي (بدون عرض النص)
                    audio_file = "faza_audio.mp3"
                    asyncio.run(generate_natural_audio(generated_script, audio_file))
                    
                    # 3. عرض النتيجة (صوت فقط)
                    st.markdown("---")
                    st.markdown("### 🎧 جاهز! اسمعي الفزعة:")
                    st.audio(audio_file)
                    
                    with open(audio_file, "rb") as f:
                        st.download_button("تحميل المحادثة MP3", f, file_name="nora_manal_session.mp3")
                        
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
    else:
        st.error("الملف غير قابل للقراءة.")
