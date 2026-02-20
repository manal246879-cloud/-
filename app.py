import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. إعدادات الصفحة والستايل ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background-color: #8A1538; color: white; border: none; font-weight: bold;
    }
    .chat-box { background-color: #f9f9f9; padding: 15px; border-radius: 15px; border-right: 5px solid #8A1538; margin-bottom: 10px; }
    h1 { color: #8A1538; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. تهيئة المفاتيح ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = models[0] if models else "gemini-pro"
except:
    st.error("⚠️ تأكدي من المفاتيح في Secrets")
    st.stop()

# المعرفات الخاصة بك
VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة تحويل النص لصوت (محسنة لتكون بشرية أكثر) ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,           # تقليل الثبات يجعل الصوت أكثر تعبيراً
            "similarity_boost": 0.8,    # زيادة التشابه مع الصوت الأصلي
            "style": 0.5,               # إضافة نبرة حيوية
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
    full_text = "".join([p.extract_text() for p in reader.pages[:5] if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز!")
        col1, col2, col3 = st.columns(3)
        
        prompt_type = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            prompt_type = "اشرحي المحتوى بلهجة نجدية كأنها سوالف بنات حقيقية، استخدمي كلمات مثل 'تخيلي، شوفي، يعني، صراحة'. الحوار بين سارة ونورة."
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            prompt_type = "ترجمي واشرحي بلهجة نجدية سوالف بنات (سارة ونورة) بشكل عفوي وسريع."
        if col3.button("🇬🇧 English"):
            prompt_type = "Explain as a natural, fast-paced English dialogue between Sarah and Nora."

        if prompt_type:
            with st.spinner("جاري تحضير السالفة... ☕"):
                model = genai.GenerativeModel(WORKING_MODEL)
                res = model.generate_content([
                    f"أنتِ سارة ونورة. حولي هذا النص لسوالف عفوية جداً وبشرية. التنسيق: سارة: [نص] نورة: [نص]. المحتوى: {full_text[:5000]}",
                    "اجعلي الحوار 8 تبادلات سريعة."
                ])
                
                lines = [l for l in res.text.split('\n') if ':' in l]
                
                all_audio = b"" # لجمع كل المقاطع هنا
                
                st.markdown("### 📝 نص الحوار:")
                for line in lines:
                    name, speech = line.split(':', 1)
                    # إظهار النص على الشاشة
                    st.markdown(f"<div class='chat-box'><b>{name}:</b> {speech}</div>", unsafe_allow_html=True)
                    
                    # تحويل للصوت وجمعه
                    vid = VOICE_ID_1 if "سارة" in name or "Sarah" in name else VOICE_ID_2
                    audio_clip = get_audio_clip(speech.strip(), vid)
                    if audio_clip:
                        all_audio += audio_clip # دمج ملفات الصوت

                if all_audio:
                    st.markdown("### 🎧 استمعي للسالفة كاملة:")
                    st.audio(all_audio, format="audio/mp3")
                    st.balloons()
