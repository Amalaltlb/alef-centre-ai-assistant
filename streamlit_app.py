# -*- coding: utf-8 -*-
import streamlit as st
import random
from urllib.parse import quote

# 1) اعداد صفحة ستريمليت
#st.set_page_config(page_title="Alef Centre - مساعد ذكي", page_icon="🧠", layout="wide")

# 2) تفعيل RTL + خط عربي
st.markdown("""
<style>
/* اجعل الاتجاه يمين -> يسار */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
  direction: rtl;
}
/* محاذاة النصوص */
[data-testid="stMarkdownContainer"], .stAlert, .stExpander, .stButton, .stText, .stSubheader, .stHeader {
  text-align: right;
}
/* الحقول */
input, textarea { direction: rtl !important; text-align: right !important; }
/* العناوين والقوائم */
h1, h2, h3, h4, h5, p, ul, ol, li { text-align: right; }
/* عناصر نريدها LTR عند الحاجة (روابط/اكواد) */
.ltr, a code, code { direction: ltr !important; text-align: left !important; unicode-bidi: embed; }
/* خط عربي */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] * { font-family: "Tajawal", sans-serif; }
</style>
""", unsafe_allow_html=True)

# 3) بيانات المساعد
CLINIC_NAME = "Alef Centre"

SERVICES = {
    "جلسة فحص ارلن اولية": 350,
    "تشخيص ارلن كامل": 900,
    "متابعة وتعديل العدسات": 250,
    "دعم تعليمي وصعوبات تعلم": 300,
    "جلسة نطق وتخاطب": 300
}

ADDRESS_AR = "شارع الوصل، مبنى الفردوس 4، الطابق الاول، مكتب 133، دبي، الامارات العربية المتحدة"
ADDRESS_EN = "Al wasl, Ferdous Building 4 1st Floor, Office 133 - Dubai - Émirats arabes unis."
MAPS_URL   = "https://www.google.com/maps/place/Alef+Centre+مركز+ألف%E2%80%AD/@25.179052,55.2299736,17z/data=!4m10!1m2!2m1!1sAl+wasl,+Ferdous+Building+4+1st+Floor,+Office+133+-+Dubai+-+United+Arab+Emirates!3m6!1s0x3e5f69dc9f93a4db:0xc26cd5a7395f530!8m2!3d25.179052!4d55.2347372!15sClBBbCB3YXNsLCBGZXJkb3VzIEJ1aWxkaW5nIDQgMXN0IEZsb29yLCBPZmZpY2UgMTMzIC0gRHViYWkgLSBVbml0ZWQgQXJhYiBFbWlyYXRlc1pMIkphbCB3YXNsIGZlcmRvdXMgYnVpbGRpbmcgNCAxc3QgZmxvb3Igb2ZmaWNlIDEzMyBkdWJhaSB1bml0ZWQgYXJhYiBlbWlyYXRlc5IBFmVkdWNhdGlvbmFsX2NvbnN1bHRhbnSaASRDaGREU1VoTk1HOW5TMFZKUTBGblNVUjBjSFF6ZHkxM1JSQUKqAZUBEAEqICIcZmVyZG91cyBidWlsZGluZyA0IDFzdCBmbG9vcigAMh8QASIbxm50P0cykL6AQF309-FThyC40yRvnHtqelh9Mk4QAiJKYWwgd2FzbCBmZXJkb3VzIGJ1aWxkaW5nIDQgMXN0IGZsb29yIG9mZmljZSAxMzMgZHViYWkgdW5pdGVkIGFyYWIgZW1pcmF0ZXPgAQD6AQQIABA6!16s%2Fg%2F11fmsfdp21?hl=fr&entry=ttu&g_ep=EgoyMDI1MDkyMS4wIKXMDSoASAFQAw%3D%3D"

HOURS = {
    "الاحد - الخميس": "10:00 - 17:30",
    "الجمعة": "مغلق",
    "السبت": "مغلق"
}

PHONES = ["+971 4 388 1169", "+971 56 778 3020"]
EMAILS = ["info@alefcentre.com", "alefcentre@gmail.com"]

# 4) واجهة التطبيق
st.title(f"🧠 {CLINIC_NAME} - مساعد ذكي (عرض تجريبي)")
st.caption("واجهة عربية فقط. هذا ديمو للتجربة وليس نظاما نهائيا.")

st.markdown("""
**ماذا يفعل المساعد؟**
- حجز جلسة مبدئية او متابعة
- الاجابة عن الاسعار التقريبية
- عرض ساعات العمل والعنوان وطرق التواصل
- ارسال تاكيد وهمي للحجز في هذا الديمو
""")

with st.expander("طريقة الاستخدام / امثلة", expanded=False):
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

    # الموقع اولا (لمنع التقاط "كم" داخل "موقعكم")
    if has_any(t, ["موقع", "عنوان", "وين", "لوكيشن"]):
        return f"العنوان: {ADDRESS_AR}\n({ADDRESS_EN})\nرابط خرائط جوجل: {MAPS_URL}\nيمكنك استخدام الازرار في الاسفل لفتح الخريطة او ارسال اللوكيشن عبر واتساب."

    # الحجز
    if has_any(t, ["حجز", "موعد", "ارلن"]):
        slot = f"{random.choice(['10:00','12:30','15:00','16:30'])} يوم {random.choice(['الاربعاء','الخميس','الاحد'])}"
        ref  = f"REF-{random.randint(1000,9999)}"
        svc  = random.choice(list(SERVICES.keys()))
        return f"تم الحجز بنجاح. الخدمة: {svc}. الموعد: {slot}. رقم المرجع: {ref}. هذا حجز تجريبي."

    # ساعات العمل
    if has_any(t, ["ساعات", "العمل", "دوام"]):
        return f"ساعات العمل:\nالاحد - الخميس: {HOURS['الاحد - الخميس']}\nالجمعة: {HOURS['الجمعة']}\nالسبت: {HOURS['السبت']}"

    # التواصل
    if has_any(t, ["تواصل", "رقم", "واتساب", "بريد"]):
        return f"ارقام الهاتف: {', '.join(PHONES)}\nالبريد الالكتروني: {', '.join(EMAILS)}"

    # التامين
    if has_any(t, ["تامين", "تأمين"]):
        return "المركز تعليمي وتشخيصي لاضطراب ارلن ودعم التعلم، وليس عيادة طبية تقليدية. عادة لا يتم الفوترة عبر التامين الطبي. للاستفسار النهائي تواصل مع الاستقبال."

    # الاسعار
    if has_price_intent(t):
        lines = [f"- {k}: {v} درهم تقريبا" for k,v in SERVICES.items()]
        return "الاسعار التقريبية:\n" + "\n".join(lines)

    # ترحيب افتراضي
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
