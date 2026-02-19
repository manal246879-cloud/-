import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import requests # لاستدعاء ElevenLabs
import os

# --- 1. إعدادات الهوية ---
st.set_page_config(page_title="فزعة - بودكاست احترافي", page_icon="🎙️")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Tajawal', sans-serif; direction: rtl; text-align: right; }
    .stButton>button { border-radius: 30px; background-color: #8A1538; color: white; height: 4em; font-size: 18px; }
    h1 { color: #8A1538; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد المفاتيح ---
GEMINI_API_KEY = "AIzaSy..." # مفتاح جمناي الخاص بك
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY" # مفتاح ايلفن لابس الخاص بك

genai.configure(api_key=GEMINI_API_KEY)

# --- 3. دالة توليد الصوت عبر ElevenLabs ---
def generate_podcast_audio(text):
    # اخترت لك صوت "Aria" أو "Layla" لأنهن الأفضل في العربية
    # يمكنك تغيير الـ voice_id من موقعهم
    voice_id = "EXAVITQu4vr4xnSDxMaL" # مثال لصوت احترافي
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2", # هذا الموديل يدعم العربية بطلاقة
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open("podcast.mp3", "wb") as f:
            f.write(response.content)
        return "podcast.mp3"
    else:
        st.error(f"خطأ في ElevenLabs: {response.text}")
        return None

# --- 4. الواجهة ---
st.markdown("<h1>🎙️ بودكاست فزعة</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>حولي محاضراتك لسوالف ممتعة (بصوت طبيعي) 🎧</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("ارفعي ملف الـ PDF", type="pdf")

if uploaded_file:
    # قراءة الملف
    reader = PdfReader(uploaded_file)
    content = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    if content:
        if st.button("✨ ابدأي جلسة السوالف"):
            with st.spinner("نورة وسارة يجهزون المايكروفونات... 🎙️✨"):
                
                # برومبت البودكاست (Deep Dive)
                prompt = f"""
                اكتب سيناريو بودكاست تعليمي بلهجة نجدية بيضاء. 
                الشخصيات: (نورة) طالبة ذكية تسأل، و(سارة) خبيرة تشرح بأسلوب ممتع وعميق.
                الموضوع: {content}
                
                التعليمات:
                - ابدأي بـ "يا هلا والله بنورة، اليوم موضوعنا دسم بس بنبسطه.."
                - اجعلي الحوار متفاعلاً فيه "ما شاء الله"، "تخيلي"، "رهيب!".
                - الشرح يكون Deep Dive، لا تتركين ولا معلومة مهمة.
                - المحادثة يجب أن تكون نصاً واحداً متصلاً يقرأه الشخصان (كحوار).
                - لا تكتبي أسماء الشخصيات في النص النهائي، فقط الحوار مباشرة.
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                script = model.generate_content(prompt).text
                
                # تحويل السيناريو لصوت (بدون إظهار النص)
                audio_file = generate_podcast_audio(script)
                
                if audio_file:
                    st.success("جلسة السوالف جاهزة! استمتعي بالتعلم ☕🎧")
                    st.audio(audio_file)
    else:
        st.error("تأكدي من محتوى الملف.")

