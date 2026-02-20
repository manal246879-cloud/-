import streamlit as st
import google.generativeai as genai
from elevenlabs.client import ElevenLabs

st.title("🛡️ فاحص المفاتيح الذاتي")

# 1. فحص وجود المفاتيح في Secrets
st.subheader("1. فحص وجود المفاتيح")
keys = ["GEMINI_API_KEY", "ELEVENLABS_API_KEY", "VOICE_ID_1", "VOICE_ID_2"]
all_exists = True

for k in keys:
    if k in st.secrets:
        st.write(f"✅ المفتاح `{k}` موجود")
    else:
        st.error(f"❌ المفتاح `{k}` مفقود من Secrets")
        all_exists = False

if all_exists:
    if st.button("بدء فحص الصلاحية الآن"):
        # 2. فحص صلاحية جماني
        st.subheader("2. فحص اتصال جوجل (Gemini)")
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("test")
            st.success("✅ مفتاح جماني شغال 100% ورد علينا!")
        except Exception as e:
            st.error(f"❌ مشكلة في مفتاح جماني: {e}")

        # 3. فحص صلاحية اليفن لابز
        st.subheader("3. فحص اتصال اليفن لابز (ElevenLabs)")
        try:
            client = ElevenLabs(api_key=st.secrets["ELEVENLABS_API_KEY"])
            # محاولة جلب بيانات الحساب للتأكد من الرصيد والمفتاح
            user_info = client.user.get()
            st.success(f"✅ مفتاح اليفن لابز شغال! الرصيد المتبقي: {user_info.subscription.character_count}")
        except Exception as e:
            st.error(f"❌ مشكلة في مفتاح اليفن لابز: {e}")
