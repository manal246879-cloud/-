import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests
import time

# --- 1. الإعدادات والستايل ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    h1 { color: #8A1538; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المفاتيح ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    # استخدام موديل 1.5 flash لأن حدوده أعلى ومجاني
    WORKING_MODEL = "gemini-1.5-flash" 
except:
    st.error("⚠️ تأكدي من المفاتيح في Secrets")
    st.stop()

VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة تحويل النص لصوت (Turbo v2.5) ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.25,
            "similarity_boost": 0.8, 
            "style": 1.0,
            "use_speaker_boost": True
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.content if response.status_code == 200 else None

# --- 4. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if file:
    reader = PdfReader(file)
    full_text = "".join([p.extract_text() for p in reader.pages[:10] if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز!")
        col1, col2, col3 = st.columns(3)
        
        task_prompt = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task_prompt = "اشرحي ولخصي المحتوى ديب دايف بلهجة نجدية عفوية جداً (سارة ونورة). استخدمي كلمات حشو (اممم، تخيلي، وش ذاا، الزبدة)."
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task_prompt = "ترجمي المحتوى ولخصيه ديب دايف بلهجة نجدية عفوية (سارة ونورة). حولي المصطلحات الصعبة لأمثلة شعبية."
        if col3.button("🇬🇧 English"):
            task_prompt = "Deep dive explanation in a natural, fast-paced English dialogue between Sarah and Nora."

        if task_prompt:
            with st.spinner("جاري تحضير السالفة... (قد يتطلب الأمر دقيقة إذا كان الضغط عالياً) 🎧"):
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    res = model.generate_content([
                        f"أنتِ سارة ونورة. حولي النص التالي لسوالف بشرية جداً (Deep Dive). التنسيق: سارة: [نص] نورة: [نص]. المحتوى: {full_text[:7000]}",
                        task_prompt,
                        "اجعلي الحوار 8 تبادلات، وأضيفي تمديد للحروف وضحكات (ههههه) وكلمات عفوية."
                    ])
                    
                    lines = [l for l in res.text.split('\n') if ':' in l]
                    all_audio = b"" 
                    
                    for line in lines:
                        name, speech = line.split(':', 1)
                        vid = VOICE_ID_1 if "سارة" in name or "Sarah" in name else VOICE_ID_2
                        audio_clip = get_audio_clip(speech.strip() + "... ", vid)
                        if audio_clip:
                            all_audio += audio_clip

                    if all_audio:
                        st.markdown("---")
                        st.audio(all_audio, format="audio/mp3")
                        st.balloons()
                
                except Exception as e:
                    if "429" in str(e) or "quota" in str(e).lower():
                        st.error("⚠️ وصلتِ للحد الأقصى من محاولات جوجل المجانية. انتظري دقيقة واحدة فقط وجربي مرة ثانية.")
                    else:
                        st.error(f"حدث خطأ: {e}")
