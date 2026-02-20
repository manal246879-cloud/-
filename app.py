import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. الواجهة الأصلية (بدون أي تغيير) ---
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

# --- 2. تهيئة المفاتيح واختيار الموديل ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = next((m for m in available_models if "1.5-flash" in m or "pro" in m), available_models[0])
except Exception as e:
    st.error(f"⚠️ خطأ في الإعدادات: {e}")
    st.stop()

# المعرفات الخاصة بك (سارة ونورة)
VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة الصوت (إعدادات النبرة البشرية العفوية) ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.25,      # منخفض جداً لكسر الروبوتية وإضافة حماس
            "similarity_boost": 0.8, 
            "style": 1.0,           # أداء تعبيري بشري عالي
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
        # الزر الأول: عربي لعربي
        if col1.button("🇸🇦 سولفها بالعربي"):
            task_prompt = "اشرحي المحتوى ديب دايف بلهجة نجدية عفوية جداً (سارة ونورة). استخدمي جمل قصيرة وحشو بشري (اممم، يووه، تخيلي، لحظة)."
        
        # الزر الثاني: انجليزي لعربي (عربناها لك)
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task_prompt = "ترجمي المحتوى ولخصيه ديب دايف بلهجة نجدية عفوية (سارة ونورة). استخدمي جمل قصيرة وحشو بشري (من جد، اسمعي، يعني)."
        
        # الزر الثالث: انجليزي لانجليزي
        if col3.button("🇬🇧 English"):
            task_prompt = "Deep dive explanation in a natural, fast-paced English dialogue between Sarah and Nora. Use fillers like (Wait, wow, imagine, like)."

        if task_prompt:
            with st.spinner("جاري تحضير السالفة بنبرة بشرية... 🎧"):
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    res = model.generate_content([
                        f"أنتِ سارة ونورة. حولي النص التالي لسوالف بشرية عفوية جداً. التنسيق: سارة: [نص] نورة: [نص]. المحتوى: {full_text[:7000]}",
                        task_prompt,
                        "مهم: اجعلي الجمل قصيرة جداً (Punchy) وأضيفي ضحكات ومقاطعات لكسر الروبوتية."
                    ])
                    
                    lines = [l for l in res.text.split('\n') if ':' in l]
                    all_audio = b"" 
                    
                    for line in lines:
                        try:
                            name, speech = line.split(':', 1)
                            vid = VOICE_ID_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_ID_2
                            # تحويل النص لصوت مع إضافة وقفة بسيطة
                            audio_clip = get_audio_clip(speech.strip() + "... ", vid)
                            if audio_clip:
                                all_audio += audio_clip
                        except:
                            continue

                    if all_audio:
                        st.markdown("---")
                        st.audio(all_audio, format="audio/mp3")
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
