# -*- coding: utf-8 -*-
import streamlit as st
import random
from urllib.parse import quote

# 1) Page config
st.set_page_config(page_title="Alef Centre - مساعد ذكي", page_icon="🧠", layout="wide")

# 2) RTL + Arabic font + fix expander overlap
st.markdown("""
<style>
/* RTL عام */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { direction: rtl; }
[data-testid="stMarkdownContainer"], .stAlert, .stExpander, .stButton, .stText, .stSubheader, .stHeader { text-align: right; }
input, textarea { direction: rtl !important; text-align: right !important; }
h1, h2, h3, h4, h5, p, ul, ol, li { text-align: right; }

/* ✅ اصلاح تراكب عنوان الـ Expander مع الأيقونة */
[data-testid="stExpander"] > details > summary {
  direction: rtl !important;
  display: flex;
  flex-direction: row-reverse;   /* يضع السهم يسار والعنوان يمين */
  align-items: center;
}
[data-testid="stExpander"] > details > summary svg {
  margin-left: 8px; margin-right: 0;
}
[data-testid="stExpander"] > details > summary > div {
  flex: 1; text-align: right;
}

/* عناصر نريدها LTR عند الحاجة (روابط/اكواد) */
.ltr, a code, code { direction: ltr !important; text-align: left !important; unicode-bidi: embed; }

/* خط عربي مريح */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] * { font-family: "Tajawal", sans-serif; }
</style>
""", unsafe_allow_html=True)

# 3) Data
CLINIC_NAME = "Alef Centre"

SERVICES = {
    "جلسة فحص ارلن اولية": 350,
    "تشخيص ارلن كامل": 900,
    "متابعة وتعديل العدسات": 250,
    "دعم تعليمي وصعوبات تعلم": 300,
    "جلسة نطق وتخاطب": 300
}

# عناوين محدثة حسب خرائط جوجل
ADDRESS_AR = "شارع الوصل، مبنى الفردوس 4، الطابق الاول، مكتب 133، دبي، الامارات العربية المتحدة"
ADDRESS_EN = "Al wasl, Ferdous Building 4 1st Floor, Office 133 - Dubai - Émirats arabes unis."
MAPS_URL   = "https://maps.google.com/?q=Al+wasl,+Ferdous+Building+4+1st+Floor,+Office+133+-+Dubai+-+%C3%89mirats+arabes+unis."

HOURS = {
    "الاحد - الخميس": "10:00 - 17:30",
    "الجمعة": "مغلق",
    "السبت": "مغلق"
}

PHONES = ["+971 4 388 1169", "+971 56 778 3020"]
EMAILS = ["info@alefcentre.com", "alefcentre@gmail.com"]

# 4) UI
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

    # الموقع اولا
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
    if has_any(t, ["مرحبا", "ا]()_
