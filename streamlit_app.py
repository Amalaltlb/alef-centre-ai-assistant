# -*- coding: utf-8 -*-
import streamlit as st
from urllib.parse import quote, quote_plus
from datetime import datetime, date, time, timedelta
import uuid
import re
import io

# =========================
# Page & Theme
# =========================
st.set_page_config(page_title="Alef Centre — AI Assistant", page_icon="🧠", layout="wide")

st.markdown("""
<style>
/* RTL layout */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { direction: rtl; }
[data-testid="stMarkdownContainer"], .stAlert, .stExpander, .stButton, .stText, .stSubheader, .stHeader { text-align: right; }
input, textarea, select { direction: rtl !important; text-align: right !important; }
h1, h2, h3, h4, h5, p, ul, ol, li { text-align: right; margin: 0.25rem 0; }

/* Expander overlap fix */
[data-testid="stExpander"] > details > summary {
  direction: rtl !important; display: flex; flex-direction: row-reverse; align-items: center;
}
[data-testid="stExpander"] > details > summary svg { margin-left: 8px; }
[data-testid="stExpander"] > details > summary > div { flex: 1; text-align: right; }

/* Chips */
.chips { display:flex; flex-wrap:wrap; gap:8px; margin: 6px 0 2px; }
.chips a {
  display:inline-block; padding:8px 10px; border-radius:999px; background:#f1f5f9; color:#0f172a;
  text-decoration:none; font: 600 12px/1 system-ui,-apple-system,Segoe UI,Roboto,Arial;
  border:1px solid #e2e8f0;
}

/* LTR blocks for links/code */
.ltr, a code, code { direction: ltr !important; text-align: left !important; unicode-bidi: embed; }

/* Arabic font */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] * { font-family: "Tajawal", sans-serif; }
</style>
""", unsafe_allow_html=True)

# =========================
# Data
# =========================
# Business data
CLINIC_NAME = "Alef Centre"

ADDRESS_AR = "شارع الوصل، مبنى الفردوس 4، الطابق الاول، مكتب 133، دبي، الامارات العربية المتحدة"
ADDRESS_EN = "Al wasl, Ferdous Building 4 1st Floor, Office 133 - Dubai - Émirats arabes unis."
MAPS_QUERY = ADDRESS_EN
MAPS_URL   = "https://maps.google.com/?q=" + quote_plus(MAPS_QUERY)

PHONES = ["+971 4 388 1169", "+971 56 778 3020"]
EMAILS = ["info@alefcentre.com", "alefcentre@gmail.com"]

# Opening hours
WORK_DAYS = [0,1,2,3,6]  # Monday=0 ... Sunday=6  (Sun–Thu open; Fri/Sat closed)
OPEN_T, CLOSE_T = time(10, 0), time(17, 30)

SERVICES = [
    {"id":"irlen_screen",  "ar":"جلسة فحص ارلن اولية",       "en":"Irlen initial screening", "mins":30, "price":350},
    {"id":"irlen_full",    "ar":"تشخيص ارلن كامل",           "en":"Irlen full assessment",   "mins":60, "price":900},
    {"id":"lenses_follow", "ar":"متابعة وتعديل العدسات",     "en":"Lenses follow-up",        "mins":20, "price":250},
    {"id":"learning_sup",  "ar":"دعم تعليمي وصعوبات تعلم"_
