import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. الواجهة الأصلية (ممنوع اللمس) ---
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

# --- 2. اكتشاف الموديل المتاح "فعلياً" في حسابك ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    
    # جلب أي موديل متاح يدعم التوليد (عشان ما نقول اسم ويطلع غلط)
    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if not all_models:
        st.error("لا يوجد موديلات متاحة في حسابك.")
        st.stop()
    # نختار أول واحد في القائمة لأنه هو اللي غالباً يكون شغال
    WORKING_MODEL = all_models[0]
except Exception as e:
    st.error(f"⚠️ خطأ في الاتصال: {e}")
    st.stop()

VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة الصوت (بشرية غير روبوتية) ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.25,      # عفوية عالية
            "similarity_boost": 0.8, 
            "style": 1.0,           # انفعالات بشرية
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
            task_prompt = "سوالف بنات نجدية ديب دايف. جمل قصيرة جداً وحشو بشري (اممم، يووه، تخيلي، من جد)."
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task_prompt = "ترجمي ولخصي ديب دايف بلهجة نجدية عفوية (سارة ونورة). جمل قصيرة ومقاطعات."
        if col3.button("🇬🇧 English"):
            task_prompt = "Natural English deep dive dialogue between Sarah and Nora. Short sentences and fillers."

        if task_prompt:
            with st.spinner("سارة ونورة يقرأون المحاضرة... 🎧"):
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    res = model.generate_content([
                        f"أنتِ سارة ونورة. حولي النص لسوالف بشرية عفوية (Deep Dive). التنسيق: سارة: [نص] نورة: [نص]. المحتوى: {full_text[:6000]}",
                        task_prompt,
                        "مهم: جمل قصيرة جداً، ضحكات، ومقاطعات بشرية."
                    ])
                    
                    lines = [l for l in res.text.split('\n') if ':' in l]
                    all_audio = b"" 
                    
                    for line in lines:
                        try:
                            name, speech = line.split(':', 1)
                            vid = VOICE_ID_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_ID_2
                            audio_clip = get_audio_clip(speech.strip() + "... ", vid)
                            if audio_clip: all_audio += audio_clip
                        except: continue

                    if all_audio:
                        st.markdown("---")
                        st.audio(all_audio, format="audio/mp3")
                        st.balloons()
                except Exception as e:
                    if "429" in str(e):
                        st.error("⚠️ انتهت محاولات جوجل المجانية لهذا اليوم (20 طلب). جربي مرة ثانية بكرة، أو استخدمي مفتاح API جديد.")
                    else:
                        st.error(f"حدث خطأ: {e}")
