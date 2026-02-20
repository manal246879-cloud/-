import streamlit as st
from elevenlabs.client import ElevenLabs

# جلب المفاتيح
try:
    ELEVEN_KEY = st.secrets["ELEVENLABS_API_KEY"]
    VOICE_1 = st.secrets["VOICE_ID_1"]
    client = ElevenLabs(api_key=ELEVEN_KEY)
except Exception as e:
    st.error(f"المفاتيح ناقصة: {e}")

st.title("اختبار الصوت المباشر")

if st.button("اضغطي هنا لتجربة الصوت"):
    try:
        st.write("جاري محاولة توليد الصوت...")
        audio = client.generate(
            text="هلا والله، أنا سارة، هل تسمعيني؟",
            voice=VOICE_1,
            model="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(list(audio))
        if audio_bytes:
            st.audio(audio_bytes, format="audio/mp3")
            st.success("اشتغل الصوت! يعني المشكلة كانت في الملف أو جماني")
        else:
            st.error("فشل التوليد: الملف الصوتي فارغ")
    except Exception as e:
        st.error(f"فشل الاتصال بـ ElevenLabs: {e}")
        st.info("إذا طلع لك خطأ Quota Exceeded يعني رصيدك خلص")
