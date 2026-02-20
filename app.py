import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs

# --- 1. الستايل ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    h1 { color: #8A1538; text-align: center; font-family: 'Tajawal'; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    genai.configure(api_key=GEMINI_KEY)
    client = ElevenLabs(api_key=ELEVEN_KEY)
except Exception as e:
    st.error(f"❌ مشكلة في الـ Secrets: {e}")
    st.stop()

# --- 3. دالة جلب السكريبت ---
def get_script(prompt):
    # محاولة الاتصال بالموديلات المتاحة لتجنب 404
    for m_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            model = genai.GenerativeModel(m_name)
            response = model.generate_content([
                "أنتِ سارة ونورة. حولي النص لحوار سوالف بنات طبيعي. التنسيق: سارة: [نص] نورة: [نص]. اكتفي بـ 3 تبادلات.",
                prompt
            ])
            return response.text
        except: continue
    return None

# --- 4. الواجهة ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز!")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة: {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this in English dialogue between Sarah and Nora: {full_text[:6000]}"

        if task:
            with st.spinner("جاري توليد الصوت... 🎧"):
                script = get_script(task)
                
                if not script:
                    st.error("❌ فشل الاتصال بجمناي (تأكدي من مفتاح جوجل)")
                else:
                    lines = [l.strip() for l in script.split('\n') if ':' in l]
                    audio_found = False
                    
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            vid = VOICE_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_2
                            
                            # محاولة توليد الصوت
                            audio = client.generate(text=text.strip(), voice=vid, model="eleven_multilingual_v2")
                            audio_bytes = b"".join(list(audio))
                            
                            if audio_bytes:
                                st.audio(audio_bytes, format="audio/mp3")
                                audio_found = True
                        except Exception as e:
                            st.error(f"❌ فشل توليد الصوت لـ {line.split(':')[0]}: {e}")
                    
                    if audio_found:
                        st.info("اسمعي السالفة بالترتيب من الأعلى ✨")
                    else:
                        st.warning("⚠️ لم يتم توليد أي صوت. تأكدي من رصيد ElevenLabs.")
