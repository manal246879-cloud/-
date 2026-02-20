import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests

# --- 1. الإعدادات ---
st.set_page_config(page_title="فزعة - Deep Dive", page_icon="🌸")

# --- 2. تهيئة المفاتيح ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    WORKING_MODEL = models[0] if models else "gemini-pro"
except:
    st.error("⚠️ تأكدي من المفاتيح في Secrets")
    st.stop()

VOICE_ID_1 = "qi4PkV9c01kb869Vh7Su" # سارة
VOICE_ID_2 = "a1KZUXKFVFDOb33I1uqr" # نورة

# --- 3. دالة تحويل النص لصوت (إعدادات Turbo v2.5 البشرية) ---
def get_audio_clip(text, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"Accept": "audio/mpeg", "Content-Type": "application/json", "xi-api-key": ELEVEN_KEY}
    data = {
        "text": text,
        "model_id": "eleven_turbo_v2_5", # تم التغيير لأحدث وأسرع موديل بشري
        "voice_settings": {
            "stability": 0.20,           # منخفض جداً لإعطاء عفوية قصوى ومنع الرتابة
            "similarity_boost": 0.8, 
            "style": 1.0,               # أقصى درجة من الأداء التعبيري
            "use_speaker_boost": True
        }
    }
    response = requests.post(url, json=data, headers=headers)
    return response.content if response.status_code == 200 else None

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align: center; color: #8A1538;'>🌸 Deep Dive: سارة ونورة</h1>", unsafe_allow_html=True)
file = st.file_uploader("ارفعي المحاضرة (PDF)", type="pdf")

if file:
    reader = PdfReader(file)
    full_text = "".join([p.extract_text() for p in reader.pages[:10] if p.extract_text()])
    
    if full_text.strip():
        if st.button("🚀 ابدأ الديب دايف (نبرة بشرية)"):
            with st.spinner("سارة ونورة يحللون المحاضرة... 🎧"):
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    
                    # برومبت متطور لإنتاج نص "قابل للغناء" بصوت بشري
                    prompt = f"""
                    أنتِ سارة ونورة. حولي النص التالي لحوار 'Deep Dive' بلهجة نجدية عفوية جداً.
                    مهم جداً لكسر الروبوتية:
                    1. اكتبي الكلمات كما تنطق (مثلاً: 'وش ذااا'، 'يا خييي'، 'تخيللللي').
                    2. أضيفي تعبيرات صوتية مكتوبة: (ههههه، امممم، واو، يووه، لاااا).
                    3. اجعلي الجمل قصيرة وسريعة وورا بعض، مع مقاطعات عفوية.
                    4. ابدئي بصدمة وانتهي بالزبدة.
                    
                    المحتوى: {full_text[:6000]}
                    
                    التنسيق: سارة: [نص] نورة: [نص].
                    """
                    
                    res = model.generate_content(prompt)
                    lines = [l for l in res.text.split('\n') if ':' in l]
                    
                    all_audio = b"" 
                    
                    for line in lines:
                        try:
                            name, speech = line.split(':', 1)
                            vid = VOICE_ID_1 if "سارة" in name or "Sarah" in name else VOICE_ID_2
                            
                            # إضافة وقفات زمنية (صمت) بين الجمل ليعطي إيحاء بالتفكير
                            audio_clip = get_audio_clip(speech.strip() + "... ", vid)
                            if audio_clip:
                                all_audio += audio_clip
                        except:
                            continue

                    if all_audio:
                        st.markdown("---")
                        st.audio(all_audio, format="audio/mp3")
                        st.success("تم التوليد بموديل Turbo v2.5")
                except Exception as e:
                    st.error(f"حدث خطأ: {e}")
