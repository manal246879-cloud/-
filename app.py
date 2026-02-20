import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
from elevenlabs.client import ElevenLabs

# --- 1. الإعدادات والستايل ---
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
except Exception:
    st.error("⚠️ تأكدي من المفاتيح في Secrets")
    st.stop()

# --- 3. اختيار الموديل تلقائياً (لتجنب 404) ---
def get_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            if '1.5-flash' in m: return m
        return models[0]
    except: return "gemini-pro"

# --- 4. واجهة المستخدم ---
st.markdown("<h1>🌸 فزعة، تسولفها</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>ارفعي المحاضرة واسمعي السالفة ✨</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف المحاضرة (PDF)", type="pdf")

if uploaded_file:
    reader = PdfReader(uploaded_file)
    full_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
    
    if full_text.strip():
        st.success("الملف جاهز! اختاري نوع السالفة:")
        col1, col2, col3 = st.columns(3)
        
        task = ""
        if col1.button("🇸🇦 سولفها بالعربي"):
            task = f"اشرحي المحتوى بلهجة نجدية سوالف بنات بين سارة ونورة: {full_text[:6000]}"
        if col2.button("🇺🇸➡️🇸🇦 عربناها لك"):
            task = f"ترجمي واشرحي بلهجة نجدية سوالف بين سارة ونورة: {full_text[:6000]}"
        if col3.button("🇬🇧 English"):
            task = f"Explain this in English dialogue between Sarah and Nora: {full_text[:6000]}"

        if task:
            with st.spinner("قاعدين نجهز السالفة (صوت فقط)... 🎧"):
                try:
                    model = genai.GenerativeModel(get_model())
                    sys_prompt = "You are Sarah and Nora. Talk naturally. Format: Sarah: [text] Nora: [text]. Max 3 exchanges."
                    response = model.generate_content([sys_prompt, task])
                    
                    script = response.text
                    lines = [l.strip() for l in script.split('\n') if ':' in l]
                    
                    for line in lines:
                        try:
                            name, text = line.split(':', 1)
                            # تحديد أي بنت تسولف عشان نختار صوتها
                            vid = VOICE_1 if any(n in name.lower() for n in ["سارة", "sarah"]) else VOICE_2
                            
                            # توليد الصوت وتشغيله مباشرة بدون عرض النص
                            audio = client.generate(text=text.strip(), voice=vid, model="eleven_multilingual_v2")
                            
