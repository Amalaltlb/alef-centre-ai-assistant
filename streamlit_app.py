# -*- coding: utf-8 -*-
import streamlit as st
import random
from urllib.parse import quote

# -------------------------
# 1) Page config
# -------------------------
st.set_page_config(page_title="Alef Centre - مساعد ذكي", page_icon="🧠", layout="wide")

# -------------------------
# 2) RTL + Arabic font + fix expander overlap
# -------------------------
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

# -------------------------
# 3) Data
# -------------------------
CLINIC_NAME = "Alef Centre"

SERVICES = {
    "جلسة فحص ارلن اولية": 350,
    "تشخيص ارلن كامل": 900,
    "متابعة وتعديل العدسات": 250,
    "دعم تعليمي وصعوبات تعلم": 300,
    "جلسة نطق وتخاطب": 300
}

# عناوين محدثة حسب خرائط جوجل (كما زودتني)
ADDRESS_AR = "شارع الوصل، مبنى الفردوس 4، الطابق الاول، مكتب 133، دبي، الامارات العربية المتحدة"
ADDRESS_EN = "Al wasl, Ferdous Building 4 1st Floor, Office 133 - Dubai - United Arab Emirates."
MAPS_URL   = "https://maps.google.com/?q=Al+wasl,+Ferdous+Building+4+1st_
