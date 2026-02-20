import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. إعدادات الصفحة ---
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
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = models[0] if models else "gemini-pro"
except:
    st.error("⚠️ تأكدي من المفاتيح في Secrets")
    st.stop()

# المعرفات الخاصة بك
VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة تحويل النص لصوت (إعدادات الحماس والسرعة) ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.3,           # نبرة متغيرة وحماسية
            "similarity_boost": 0.8, 
            "style": 0.85,              # مبالغة في الأسلوب البشري
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
        st.success("الملف جاهز! سارة ونورة بيلخصون لك الزبدة:")
        col1, col2, col3 = st.columns(3)
        
        prompt_type = ""
        if col1.button("🇸🇦 لخصيها بالعربي"):
            prompt_type = "لخصي أهم النقاط في المحاضرة بلهجة نجدية عفوية جداً. سارة ونورة يسولفون ويعطون الزبدة 'تخيلي وش طلع أهم شيء، اسمعي الزبدة، المختصر هو'."
        if col2.button("🇺🇸➡️🇸🇦 ترجمة وتلخيص"):
            prompt_type = "ترجمي ولخصي المحتوى بلهجة نجدية سريعة. سارة تعلم نورة أهم الأشياء اللي لازم تعرفها للاختبار."
        if col3.button("🇬🇧 English Summary"):
            prompt_type = "Summarize the key points in a fast, natural English girl-talk dialogue between Sarah and Nora."

        if prompt_type:
            with st.spinner("جاري تلخيص المحاضرة وتجهيز السالفة... 🎧"):
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    # طلب التلخيص بوضوح
                    res = model.generate_content([
                        f"أنتِ سارة ونورة. لخصي أهم 5 نقاط في هذا النص بأسلوب سوالف بنات حماسي ومختصر جداً. التنسيق: سارة: [نص] نورة: [نص]. المحتوى: {full_text[:5000]}",
                        "اجعلي الحوار سريع ولا يتجاوز 6 تبادلات. ركزي على 'الزبدة' فقط."
                    ])
                    
                    lines = [l for l in res.text.split('\n') if ':' in l]
                    all_audio = b"" 
                    
                    for line in lines:
                        try:
                            name, speech = line.split(':', 1)
                            vid = VOICE_ID_1 if "سارة" in name or "Sarah" in name else VOICE_ID_2
                            # تحويل النص لصوت مع إضافة وقفة بسيطة
                            audio_clip = get_audio_clip(speech.strip() + " ... ", vid)
                            if audio_clip:
                                all_audio += audio_clip
                        except:
                            continue

                    if all_audio:
                        st.markdown("---")
                        st.markdown("### 🎧 استمعي للملخص كامل:")
                        st.audio(all_audio, format="audio/mp3")
                        st.balloons()
                        
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
