# -*- coding: utf-8 -*-
import streamlit as st
import random
from urllib.parse import quote

# اعدادات عامة
CLINIC_NAME = "Alef Centre"

SERVICES = {
    "جلسة فحص ارلن اولية": 350,
    "تشخيص ارلن كامل": 900,
    "متابعة وتعديل العدسات": 250,
    "دعم تعليمي وصعوبات تعلم": 300,
    "جلسة نطق وتخاطب": 300
}

ADDRESS_AR = "مبنى الفردوس 4، شارع الوصل، الطابق الاول، مكتب 133، الصفاء 1، جميرا، دبي"
ADDRESS_EN = "Al Ferdous 4, Al Wasl Road, First Floor, Office 133, Al Safa 1, Jumeirah, Dubai, UAE"
MAPS_URL = "https://maps.google.com/?q=Al+Ferdous+4,+Al+Wasl+Road,+Office+133,+Dubai"

HOURS = {
    "الاحد - الخميس": "10:00 - 17:30",
    "الجمعة": "مغلق",
    "السبت": "مغلق"
}

PHONES = ["+971 4 388 1169", "+971 56 778 3020"]
EMAILS = ["info@alefcentre.com", "alefcentre@gmail.com"]

st.set_page_config(page_title=f"{CLINIC_NAME} - مساعد ذكي", page_icon="🧠")
st.set_page_config(page_title="...", page_icon="🧠", layout="wide")


# ====== RTL + Arabic font ======
st.markdown("""
<style>
/* خلي التطبيق كله RTL */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  direction: rtl;
}

/* محاذاة النصوص للعربي */
[data-testid="stMarkdownContainer"], .stAlert, .stExpander, .stButton, .stText, .stSubheader, .stHeader {
  text-align: right;
}

/* حقول الإدخال */
input, textarea {
  direction: rtl !important;
  text-align: right !important;
}

/* العناوين والقوائم */
h1, h2, h3, h4, h5, p, ul, ol, li {
  text-align: right;
}

/* اجبر الروابط/الأكواد على LTR اذا احتجت (مثلا روابط طويلة) */
.ltr, a code, code {
  direction: ltr !important;
  text-align: left !important;
  unicode-bidi: embed;
}

/* خط عربي جميل (اختياري) */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] * {
  font-family: "Tajawal", sans-serif;
}
</style>
""", unsafe_allow_html=True)
# ====== /RTL ======

st.title(f"🧠 {CLINIC_NAME} - مساعد ذكي (عرض تجريبي)")
st.caption("واجهة عربية فقط. هذا ديمو للتجربة وليس نظاما نهائيا.")

st.markdown("""
**ماذا يفعل المساعد؟**
- حجز جلسة مبدئية او متابعة
- الاجابة عن الاسعار التقريبية
- عرض ساعات العمل والعنوان وطرق التواصل
- ارسال تاكيد وهمي للحجز في هذا الديمو
""")

with st.expander("طريقة الاستخدام"):
    st.write("""
اكتب رسائل مثل:
- اريد حجز جلسة فحص ارلن يوم الخميس الساعة 4
- ما هي ساعات العمل
- كم سعر التشخيص الكامل
- اين موقعكم
- اريد رقم التواصل
""")

def has_any(text, keywords):
    return any(k in text for k in keywords)

def has_price_intent(text):
    t = text.strip()
    if "سعر" in t or "الاسعار" in t:
        return True
    words = t.replace("؟"," ").replace("?"," ").split()
    if "كم" in words:
        return True
    if "كم سعر" in t or "بكم" in t:
        return True
    return False

def handle_message(msg: str) -> str:
    t = (msg or "").strip()

    # 1) الموقع اولا (لمنع التقاط "كم" داخل "موقعكم")
    if has_any(t, ["موقع", "عنوان", "وين", "لوكيشن"]):
        return f"العنوان: {ADDRESS_AR}\n({ADDRESS_EN})\nرابط خرائط جوجل: {MAPS_URL}\nيمكنك استخدام الازرار في الاسفل لفتح الخريطة او ارسال اللوكيشن عبر واتساب."

    # 2) الحجز
    if has_any(t, ["حجز", "موعد", "ارلن"]):
        slot = f"{random.choice(['10:00','12:30','15:00','16:30'])} يوم {random.choice(['الاربعاء','الخميس','الاحد'])}"
        ref = f"REF-{random.randint(1000,9999)}"
        svc = random.choice(list(SERVICES.keys()))
        return f"تم الحجز بنجاح. الخدمة: {svc}. الموعد: {slot}. رقم المرجع: {ref}. هذا حجز تجريبي."

    # 3) ساعات العمل
    if has_any(t, ["ساعات", "العمل", "دوام"]):
        return f"ساعات العمل:\nالاحد - الخميس: {HOURS['الاحد - الخميس']}\nالجمعة: {HOURS['الجمعة']}\nالسبت: {HOURS['السبت']}"

    # 4) التواصل
    if has_any(t, ["تواصل", "رقم", "واتساب", "بريد"]):
        return f"ارقام الهاتف: {', '.join(PHONES)}\nالبريد الالكتروني: {', '.join(EMAILS)}"

    # 5) التامين
    if has_any(t, ["تامين", "تأمين"]):
        return "المركز تعليمي وتشخيصي لاضطراب ارلن ودعم التعلم، وليس عيادة طبية تقليدية. عادة لا يتم الفوترة عبر التامين الطبي. للاستفسار النهائي تواصل مع الاستقبال."

    # 6) الاسعار
    if has_price_intent(t):
        lines = [f"- {k}: {v} درهم تقريبا" for k,v in SERVICES.items()]
        return "الاسعار التقريبية:\n" + "\n".join(lines)

    # 7) ترحيب افتراضي
    if has_any(t, ["مرحبا", "السلام", "اهلا"]):
        return "اهلا بك. اسأل عن الحجز او الاسعار او ساعات العمل او الموقع او التواصل."
    return "مفهوم. يمكنك ان تقول: حجز، الاسعار، ساعات العمل، الموقع، التواصل."

user = st.text_input("اكتب رسالتك هنا")
send = st.button("ارسال")
if send or user:
    if user:
        st.write(f"**انت:** {user}")
        st.success(handle_message(user))

st.subheader("معلومات سريعة")
st.write(f"ساعات العمل: الاحد - الخميس {HOURS['الاحد - الخميس']}")
st.write(f"العنوان: {ADDRESS_AR}")
st.write(f"الهاتف: {', '.join(PHONES)}")
st.write(f"البريد: {', '.join(EMAILS)}")

st.markdown("---")
st.subheader("روابط سريعة")
st.markdown(f"[فتح العنوان في خرائط جوجل]({MAPS_URL})")
wa_text = f"لوكيشن Alef Centre:\\n{ADDRESS_AR}\\n{MAPS_URL}"
wa_link = "https://wa.me/?text=" + quote(wa_text)
st.markdown(f"[ارسال اللوكيشن عبر واتساب]({wa_link})")
