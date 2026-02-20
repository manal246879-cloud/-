import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="فزعة، تسولفها", page_icon="🌸", layout="centered")

# --- 2. تهيئة المفاتيح ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    VOICE_2 = st.secrets["VOICE_ID_2"]
    
    genai.configure(api_key=GEMINI_KEY)
    client = ElevenLabs(api_key=ELEVEN_KEY)
except Exception as e:
    st.error(f"❌ مشكلة في Secrets: {e}")
    st.stop()

# --- 3. وظيفة اختيار الموديل المتاح تلقائياً (حل الـ 404) ---
@st.cache_resource
def get_available_model():
    try:
        # نسأل جوجل: وش الموديلات اللي مسموحة لهذا المفتاح؟
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # نفضل 1.5-flash إذا كان موجود، وإذا لا نأخذ أول واحد متاح
        for m in models:
            if '1.5-flash' in m:
                return m
        return models[0] if models else "gemini-pro"
    except Exception as e:
        return "gemini-pro"

# --- 4. واجهة المستخدم ---
st.markdown("<h1 style='text-align: center; color: #8A1538;'>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("تم الاتصال بنجاح! ✅")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة: {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this in English dialogue between Sarah and Nora: {full_text[:6000]}"

        if task:
            with st.spinner("قاعدين نضبط السالفة... ☕"):
                try:
                    # نستخدم الموديل اللي لقيناه شغال في حسابك
                    working_model = get_available_model()
                    model = genai.GenerativeModel(working_model)
                    
                    response = model.generate_content([
                        "Format: Sarah: [text] Nora: [text]. Max 3 exchanges.",
                        task
                    ])
                    
                    script = response.text
                    lines = [l.strip() for l in script.split('\n') if ':' in l]
                    
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            vid = VOICE_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_2
                            st.write(f"**{name}:** {text}")
                            
                            # توليد الصوت
                            audio = client.generate(text=text.strip(), voice=vid, model="eleven_multilingual_v2")
                            st.audio(b"".join(list(audio)), format="audio/mp3")
                        except: continue
                        
                except Exception as e:
                    st.error("⚠️ خطأ في التواصل مع جوجل:")
                    st.code(str(e))
