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
