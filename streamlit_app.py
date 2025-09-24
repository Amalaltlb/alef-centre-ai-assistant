# -*- coding: utf-8 -*-
import streamlit as st
from urllib.parse import quote
from datetime import datetime, date, time, timedelta
import uuid, re, io

# =========================
# Branding (set your real logo URL here)
# =========================
LOGO_URL = " "  # ✅ replace with real logo URL if you have it

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Alef Centre — AI Assistant",
    page_icon=(LOGO_URL if LOGO_URL else " "),
    layout="wide",
)

# =========================
# Language (AR default) + fallback
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ar"
try:
    lang = st.segmented_control("اللغة / Language", options=["ar","en"], default="ar", label_visibility="collapsed")
except Exception:
    lang = st.radio("Language", options=["ar","en"], horizontal=True, label_visibility="collapsed")
st.session_state.lang = lang

# =========================
# CSS (RTL for AR, LTR for EN) + numeric alignment helpers
# =========================
COMMON_CSS = """
<style>
/* Chips buttons look */
.chip-btn > button {
  border-radius: 999px !important;
  border: 1px solid #e2e8f0 !important;
  background: #f8fafc !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  padding: 6px 12px !important;
  margin: 0 8px 8px 0 !important;
}
.ltr-inline { direction:ltr; unicode-bidi:isolate; }  /* keeps numbers left-to-right inside Arabic lines */
</style>
"""
st.markdown(COMMON_CSS, unsafe_allow_html=True)

CSS_RTL = """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { direction: rtl; }
[data-testid="stMarkdownContainer"], .stAlert, .stExpander, .stButton, .stText, .stSubheader, .stHeader { text-align: right; }
input, textarea, select { direction: rtl !important; text-align: right !important; }
h1, h2, h3, h4, h5, p, ul, ol, li { text-align: right; margin: 0.25rem 0; }
/* Expander fix */
[data-testid="stExpander"] > details > summary { direction: rtl !important; display:flex; flex-direction:row-reverse; align-items:center; }
[data-testid="stExpander"] > details > summary svg { margin-left:8px; }
[data-testid="stExpander"] > details > summary > div { flex:1; text-align:right; }
/* Arabic font */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] * { font-family: "Tajawal", sans-serif; }
</style>
"""

CSS_LTR = """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { direction: ltr; }
[data-testid="stMarkdownContainer"], .stAlert, .stExpander, .stButton, .stText, .stSubheader, .stHeader { text-align: left; }
input, textarea, select { direction: ltr !important; text-align: left !important; }
h1, h2, h3, h4, h5, p, ul, ol, li { text-align: left; margin: 0.25rem 0; }
/* Expander fix */
[data-testid="stExpander"] > details > summary { direction: ltr !important; display:flex; flex-direction:row; align-items:center; }
[data-testid="stExpander"] > details > summary svg { margin-right:8px; }
[data-testid="stExpander"] > details > summary > div { flex:1; text-align:left; }
/* Same font works for EN too */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;600;700&display=swap');
html, body, [data-testid="stAppViewContainer"] * { font-family: "Tajawal", sans-serif; }
</style>
"""
st.markdown(CSS_RTL if lang == "ar" else CSS_LTR, unsafe_allow_html=True)

# =========================
# Business data
# =========================
CLINIC_NAME = "Alef Centre"
ADDRESS_AR = "شارع الوصل، مبنى الفردوس 4، الطابق الاول، مكتب 133، دبي، الامارات العربية المتحدة"
ADDRESS_EN = "Al wasl, Ferdous Building 4 1st Floor, Office 133 - Dubai - Émirats arabes unis."
MAPS_URL   = "https://www.google.ae/maps/place/Alef+Centre+%D9%85%D8%B1%D9%83%D8%B2+%D8%A3%D9%84%D9%81%E2%80%AD/@25.1790568,55.2321623,16z/data=!3m1!4b1!4m6!3m5!1s0x3e5f69dc9f93a4db:0xc26cd5a7395f530!8m2!3d25.179052!4d55.2347372!16s%2Fg%2F11fmsfdp21?entry=ttu&g_ep=EgoyMDI1MDkyMS4wIKXMDSoASAFQAw%3D%3D"
PHONES = ["+971 4 388 1169", "+971 56 778 3020"]
EMAILS = ["info@alefcentre.com", "alefcentre@gmail.com"]

# Opening hours (Sun–Thu)
WORK_DAYS = [6,0,1,2,3]  # Sun=6
OPEN_T, CLOSE_T = time(10, 0), time(17, 30)

SERVICES = [
    {"id":"irlen_screen",  "ar":"جلسة فحص ارلن اولية",       "en":"Irlen initial screening", "mins":30, "price":350},
    {"id":"irlen_full",    "ar":"تشخيص ارلن كامل",           "en":"Irlen full assessment",   "mins":60, "price":900},
    {"id":"lenses_follow", "ar":"متابعة وتعديل العدسات",     "en":"Lenses follow-up",        "mins":20, "price":250},
    {"id":"learning_sup",  "ar":"دعم تعليمي وصعوبات تعلم",   "en":"Learning support",        "mins":45, "price":300},
    {"id":"speech",        "ar":"جلسة نطق وتخاطب",           "en":"Speech & language",       "mins":45, "price":300},
]

# =========================
# Translations
# =========================
T = {
  "ar": {
    "title": f" {CLINIC_NAME} - مساعد ذكي (عرض تجريبي)",
    "subtitle": "هذه نسخة للتجربة قبل التركيب على واتساب/الموقع.",
    "tabs": ["الدردشة","الحجز","المعلومات"],
    "chips": ["اين موقعكم","اريد رقم التواصل","ما هي ساعات العمل","كم سعر التشخيص الكامل","اريد الحجز اليوم"],
    "ask": "اكتب سؤالك هنا",
    "send": "ارسال",
    "faq": "اسئلة سريعة",
    "hours": "ساعات العمل",
    "phones": "الهاتف",
    "emails": "البريد",
    "address": "العنوان",
    "maps": "فتح العنوان في خرائط جوجل",
    "copy": "نسخ العنوان",
    "whatsapp_loc": "ارسال اللوكيشن عبر واتساب",
    "call_now": "اتصال الآن",
    "request_call": "اطلب مكالمة",
    "callback_thanks": "تم استلام طلبك. سيتواصل معك الموظف قريبًا.",
    "booking_title": "حجز موعد",
    "svc": "الخدمة",
    "date": "اليوم",
    "time": "الوقت",
    "name": "الاسم",
    "phone": "رقم الهاتف (UAE/Intl)",
    "notes": "ملاحظة (اختياري)",
    "confirm": "تأكيد الحجز",
    "confirming": "تأكيد",
    "booking_ok": "تم الحجز بنجاح",
    "ref": "رقم المرجع",
    "ics": "تحميل تذكرة الموعد (ICS)",
    "errors": {
        "svc": "الرجاء اختيار الخدمة.",
        "date": "اختر يوم عمل (الاحد الى الخميس).",
        "time": "اختر وقت داخل الدوام.",
        "name": "اكتب اسمك.",
        "phone": "الرجاء إدخال رقم صحيح يبدأ بـ +971 أو 0."
    },
    "quick_info": "معلومات سريعة",
    "what_do": "ماذا يفعل المساعد؟",
    "what_do_bullets": [
        "حجز جلسة مبدئية او متابعة",
        "الاجابة عن الاسعار التقريبية",
        "عرض ساعات العمل والعنوان وطرق التواصل",
        "ارسال تاكيد وتذكرة الموعد (ICS) - ديمو"
    ],
    "privacy": "بالارسال انت توافق على استلام رسائل حول مواعيدك. يمكن حذف البيانات عند الطلب.",
    "human_handoff": "هل تود تحويلك لموظف؟"
  },
  "en": {
    "title": f" {CLINIC_NAME} — Smart Assistant (Demo)",
    "subtitle": "Arabic-first demo. Can be embedded into WhatsApp/website.",
    "tabs": ["Chat","Booking","Info"],
    "chips": ["Where is your location?","I need a contact number","What are opening hours?","How much is full assessment?","Book today"],
    "ask": "Type your question here",
    "send": "Send",
    "faq": "Quick replies",
    "hours": "Opening hours",
    "phones": "Phones",
    "emails": "Emails",
    "address": "Address",
    "maps": "Open in Google Maps",
    "copy": "Copy address",
    "whatsapp_loc": "Share location via WhatsApp",
    "call_now": "Call now",
    "request_call": "Request a callback",
    "callback_thanks": "Thanks, a staff member will reach out.",
    "booking_title": "Book an appointment",
    "svc": "Service",
    "date": "Date",
    "time": "Time",
    "name": "Full name",
    "phone": "Phone (UAE/Intl)",
    "notes": "Notes (optional)",
    "confirm": "Confirm booking",
    "confirming": "Confirm",
    "booking_ok": "Booking confirmed",
    "ref": "Reference",
    "ics": "Download calendar invite (ICS)",
    "errors": {
        "svc": "Please select a service.",
        "date": "Choose a working day (Sun–Thu).",
        "time": "Pick a time within opening hours.",
        "name": "Please enter your name.",
        "phone": "Phone must start with +971 or 0."
    },
    "quick_info": "Quick info",
    "what_do": "What can it do?",
    "what_do_bullets": [
        "Initial or follow-up booking",
        "Approximate pricing answers",
        "Hours, address & contact info",
        "Sends confirmation & ICS ticket (demo)"
    ],
    "privacy": "By messaging you consent to receive appointment-related messages. Data can be deleted upon request.",
    "human_handoff": "Would you like a human to take over?"
  }
}

# =========================
# Helpers
# =========================
def is_workday(d: date) -> bool:
    return d.weekday() in WORK_DAYS

def valid_phone(p: str) -> bool:
    if not p: return False
    p = p.strip().replace(" ", "")
    return bool(re.match(r"^(\+971|0)\d{8,9}$", p))

def round_up_to_quarter(dt: datetime) -> datetime:
    return dt.replace(second=0, microsecond=0, minute=(dt.minute//15+1)*15 if dt.minute%15 else dt.minute)

def gen_slots(d: date, duration_minutes: int):
    """Generate slots within opening hours; skip past times today."""
    if not is_workday(d): return []
    now = datetime.now()
    start_dt = datetime.combine(d, OPEN_T)
    if d == date.today() and now.time() > OPEN_T:
        if now.minute % 15:  # round up to next quarter-hour
            start_dt = round_up_to_quarter(now)
        else:
            start_dt = now
    end_dt = datetime.combine(d, CLOSE_T)
    step = timedelta(minutes=max(15, duration_minutes))
    slots, cur = [], start_dt
    while cur + timedelta(minutes=duration_minutes) <= end_dt:
        slots.append(cur.time())
        cur += step
    return slots

def ics_bytes(title: str, start_dt: datetime, duration_min: int, location: str, desc: str):
    end_dt = start_dt + timedelta(minutes=duration_min)
    def fmt(dt): return dt.strftime("%Y%m%dT%H%M%S")
    uid = str(uuid.uuid4())
    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Alef Centre//AI Assistant//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{fmt(datetime.utcnow())}Z
DTSTART:{fmt(start_dt)}
DTEND:{fmt(end_dt)}
SUMMARY:{title}
LOCATION:{location}
DESCRIPTION:{desc}
END:VEVENT
END:VCALENDAR
"""
    return io.BytesIO(ics.encode("utf-8"))

def tel_href(phone: str) -> str:
    digits = re.sub(r"[^+\d]", "", phone or "")
    return f"tel:{digits or '+97143881169'}"

def quick_answer(user_text: str, lang="ar") -> str:
    t = (user_text or "").strip()
    # Location
    if any(k in t for k in (["موقع","عنوان","وين","لوكيشن"] if lang=="ar" else ["where","address","location"])):
        return (f"العنوان: {ADDRESS_AR}\n({ADDRESS_EN})\nرابط خرائط جوجل: {MAPS_URL}"
                if lang=="ar" else
                f"Address: {ADDRESS_EN}\n(AR: {ADDRESS_AR})\nGoogle Maps: {MAPS_URL}")
    # Contact
    if any(k in t for k in (["تواصل","رقم","واتساب","هاتف"] if lang=="ar" else ["phone","number","contact","whatsapp"])):
        return (f"ارقام الهاتف: {', '.join(PHONES)}\nالبريد الالكتروني: {', '.join(EMAILS)}"
                if lang=="ar" else
                f"Phones: {', '.join(PHONES)}\nEmails: {', '.join(EMAILS)}")
    # Hours
    if any(k in t for k in (["ساعات","العمل","دوام"] if lang=="ar" else ["hours","opening","open"])):
        return (f"ساعات العمل: الاحد - الخميس {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (الجمعة والسبت مغلق)"
                if lang=='ar' else
                f"Hours: Sun–Thu {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (Fri & Sat closed)")
    # Pricing (avoid matching 'كم' inside 'موقعكم')
    words = t.replace("؟"," ").replace("?"," ").split()
    if ("سعر" in t or "الاسعار" in t or "كم سعر" in t or "بكم" in t or ("كم" in words)) or \
       (lang=="en" and ("price" in t or "cost" in t)):
        if lang=="ar":
            lines = [f"- {s['ar']}: {s['price']} درهم تقريبا" for s in SERVICES]
            return "الاسعار التقريبية:\n" + "\n".join(lines)
        else:
            lines = [f"- {s['en']}: ~{s['price']} AED" for s in SERVICES]
            return "Approximate pricing:\n" + "\n".join(lines)
    # Booking mention
    if any(k in t for k in (["حجز","موعد","ارلن"] if lang=="ar" else ["book","appointment","irlen"])):
        return T[lang]["human_handoff"] + " → " + (T[lang]["booking_title"])
    # Greeting
    if any(k in t for k in (["مرحبا","السلام","اهلا"] if lang=="ar" else ["hi","hello","hey"])):
        return T[lang]["what_do"] + "\n- " + "\n- ".join(T[lang]["what_do_bullets"])
    # Fallback
    return ( "مفهوم. اسأل عن: الموقع، رقم التواصل، ساعات العمل، الاسعار، او ابدأ بالحجز."
             if lang=="ar" else
             "Got it. Ask about: address, contact, hours, pricing — or start a booking." )

# =========================
# Header (logo + title)
# =========================
col_logo, col_title = st.columns([1, 6])
with col_logo:
    if LOGO_URL:
        try:
            st.image(LOGO_URL, width=56)
        except Exception:
            pass
with col_title:
    st.title(T[lang]["title"])
    st.caption(T[lang]["subtitle"])

# =========================
# Tabs
# =========================
tab_chat, tab_book, tab_info = st.tabs(T[lang]["tabs"])

# -------------------------
# Quick replies renderer (buttons, not links)
# -------------------------
def render_quick_replies(chips):
    cols = st.columns(min(4, len(chips)))  # responsive rows
    for i, c in enumerate(chips):
        with cols[i % len(cols)]:
            # wrapper class to style buttons as chips
            st.markdown('<div class="chip-btn">', unsafe_allow_html=True)
            if st.button(c, key=f"chip_{lang}_{i}"):
                st.session_state["chat_in"] = c
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# TAB: Chat
# -------------------------
with tab_chat:
    st.markdown(f"**{T[lang]['faq']}**")
    render_quick_replies(T[lang]["chips"])

    user = st.text_input(T[lang]["ask"], value=st.session_state.get("chat_in",""), key="chat_in_box")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(T[lang]["send"], use_container_width=True):
            if user:
                st.write(f"**انت:** {user}" if lang=="ar" else f"**You:** {user}")
                st.success(quick_answer(user, lang=lang))
    with c2:
        if st.button(T[lang]["request_call"], use_container_width=True):
            with st.form("callback"):
                name_cb = st.text_input(T[lang]["name"])
                phone_cb = st.text_input(T[lang]["phone"])
                ok = st.form_submit_button(T[lang]["confirming"])
                if ok:
                    if not name_cb.strip():
                        st.error(T[lang]["errors"]["name"]); st.stop()
                    if not valid_phone(phone_cb):
                        st.error(T[lang]["errors"]["phone"]); st.stop()
                    st.info(T[lang]["callback_thanks"])

    st.markdown("---")
    st.subheader(T[lang]["quick_info"])

    if lang == "ar":
        times_html = f"<span class='ltr-inline'>{OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')}</span>"
        st.markdown(f"**{T['ar']['hours']}**: الاحد - الخميس {times_html} (الجمعة والسبت مغلق)", unsafe_allow_html=True)
        st.write(f"**{T['ar']['address']}**: {ADDRESS_AR}")
        st.markdown(f"[{T['ar']['maps']}]({MAPS_URL})")
        phones_html = f"<span class='ltr-inline'>{', '.join(PHONES)}</span>"
        st.markdown(f"**{T['ar']['phones']}**: {phones_html}", unsafe_allow_html=True)
        emails_html = f"<span class='ltr-inline'>{', '.join(EMAILS)}</span>"
        st.markdown(f"**{T['ar']['emails']}**: {emails_html}", unsafe_allow_html=True)
    else:
        st.write(f"**{T['en']['hours']}**: Sun–Thu {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (Fri & Sat closed)")
        st.write(f"**{T['en']['address']}**: {ADDRESS_EN}")
        st.markdown(f"[{T['en']['maps']}]({MAPS_URL})")
        st.write(f"**{T['en']['phones']}**: {', '.join(PHONES)}")
        st.write(f"**{T['en']['emails']}**: {', '.join(EMAILS)}")

    # copy / WhatsApp / call
    cA, cB, cC = st.columns(3)
    with cA:
        if st.button(T[lang]["copy"], use_container_width=True):
            st.markdown(f"""
            <script>
            navigator.clipboard.writeText("{(ADDRESS_AR if lang=='ar' else ADDRESS_EN).replace('"','\\"')}\\n{MAPS_URL}");
            </script>
            """, unsafe_allow_html=True)
            st.toast("تم النسخ" if lang=="ar" else "Copied")
    with cB:
        wa_text = f"{'لوكيشن Alef Centre' if lang=='ar' else 'Alef Centre location'}:\\n" \
                  f"{ADDRESS_AR if lang=='ar' else ADDRESS_EN}\\n{MAPS_URL}"
        try:
            st.link_button(T[lang]["whatsapp_loc"], "https://wa.me/?text=" + quote(wa_text), use_container_width=True)
        except Exception:
            st.markdown(f"[{T[lang]['whatsapp_loc']}]({'https://wa.me/?text=' + quote(wa_text)})")
    with cC:
        try:
            st.link_button(T[lang]["call_now"], "tel:+97143881169", use_container_width=True)
        except Exception:
            st.markdown(f"[{T[lang]['call_now']}](tel:+97143881169)")

    st.caption(T[lang]["privacy"])

# -------------------------
# TAB: Booking
# -------------------------
def service_names():
    return [s["ar"] if lang=="ar" else s["en"] for s in SERVICES]

with tab_book:
    st.subheader(T[lang]["booking_title"])

    svc_choice = st.selectbox(T[lang]["svc"], options=["—"] + service_names(), index=0)
    chosen = next((s for s in SERVICES if s["ar"]==svc_choice or s["en"]==svc_choice), None)

    today = date.today()
    picked_day = st.date_input(T[lang]["date"], value=today, min_value=today)

    slots = gen_slots(picked_day, chosen["mins"] if chosen else 30)
    slot_labels = [t.strftime("%H:%M") for t in slots]
    if not slot_labels:
        st.info("لا توجد اوقات متاحة لهذا اليوم. اختر يومًا آخر." if lang=="ar" else "No times available for this date. Please choose another day.")
    slot_choice = st.selectbox(T[lang]["time"], options=["—"] + slot_labels, index=0)

    colx, coly = st.columns(2)
    with colx:
        name = st.text_input(T[lang]["name"])
    with coly:
        phone = st.text_input(T[lang]["phone"])
    notes = st.text_area(T[lang]["notes"])

    if st.button(T[lang]["confirm"], type="primary", use_container_width=True):
        if not chosen:
            st.error(T[lang]["errors"]["svc"]); st.stop()
        if not is_workday(picked_day):
            st.error(T[lang]["errors"]["date"]); st.stop()
        if slot_choice == "—":
            st.error(T[lang]["errors"]["time"]); st.stop()
        if not name.strip():
            st.error(T[lang]["errors"]["name"]); st.stop()
        if not valid_phone(phone):
            st.error(T[lang]["errors"]["phone"]); st.stop()

        chosen_time = datetime.combine(picked_day, datetime.strptime(slot_choice, "%H:%M").time())
        ref = "REF-" + str(uuid.uuid4())[:8].upper()

        st.success(f"{T[lang]['booking_ok']} — {T[lang]['ref']}: {ref}")
        st.write(f"**{T[lang]['svc']}**: {svc_choice}")
        st.write(f"**{T[lang]['date']}**: {picked_day.strftime('%Y-%m-%d')}")
        st.write(f"**{T[lang]['time']}**: {slot_choice}")
        st.write(f"**{T[lang]['name']}**: {name}")
        st.write(f"**{T[lang]['phone']}**: {phone}")
        if notes.strip():
            st.write(f"**{T[lang]['notes']}**: {notes}")

        title = f"{CLINIC_NAME} — {svc_choice}"
        desc  = f"Ref: {ref} | Phone: {phone}"
        ics = ics_bytes(title, chosen_time, chosen["mins"], ADDRESS_EN, desc)
        st.download_button(T[lang]["ics"], data=ics, file_name=f"{ref}.ics", mime="text/calendar")

        confirm_text = (f"تم حجز موعدك في {CLINIC_NAME}.\n"
                        f"الخدمة: {svc_choice}\nالتاريخ: {picked_day} - الوقت: {slot_choice}\n"
                        f"المرجع: {ref}\nالعنوان: {ADDRESS_AR}\n{MAPS_URL}") if lang=="ar" else \
                       (f"Your appointment at {CLINIC_NAME} is booked.\n"
                        f"Service: {svc_choice}\nDate: {picked_day} - Time: {slot_choice}\n"
                        f"Ref: {ref}\nAddress: {ADDRESS_EN}\n{MAPS_URL}")
        try:
            st.link_button("مشاركة التاكيد في واتساب" if lang=="ar" else "Share confirmation on WhatsApp",
                           "https://wa.me/?text=" + quote(confirm_text), use_container_width=True)
        except Exception:
            st.markdown(f"[{'مشاركة التاكيد في واتساب' if lang=='ar' else 'Share confirmation on WhatsApp'}]({'https://wa.me/?text=' + quote(confirm_text)})")

# -------------------------
# TAB: Info
# -------------------------
with tab_info:
    st.subheader(T[lang]["quick_info"])
    if lang == "ar":
        times_html = f"<span class='ltr-inline'>{OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')}</span>"
        st.markdown(f"**{T['ar']['hours']}**: الاحد - الخميس {times_html} (الجمعة والسبت مغلق)", unsafe_allow_html=True)
        st.write(f"**{T['ar']['address']}**: {ADDRESS_AR}")
        st.markdown(f"[{T['ar']['maps']}]({MAPS_URL})")
        phones_html = f"<span class='ltr-inline'>{', '.join(PHONES)}</span>"
        st.markdown(f"**{T['ar']['phones']}**: {phones_html}", unsafe_allow_html=True)
        emails_html = f"<span class='ltr-inline'>{', '.join(EMAILS)}</span>"
        st.markdown(f"**{T['ar']['emails']}**: {emails_html}", unsafe_allow_html=True)
    else:
        st.write(f"**{T['en']['hours']}**: Sun–Thu {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (Fri & Sat closed)")
        st.write(f"**{T['en']['address']}**: {ADDRESS_EN}")
        st.markdown(f"[{T['en']['maps']}]({MAPS_URL})")
        st.write(f"**{T['en']['phones']}**: {', '.join(PHONES)}")
        st.write(f"**{T['en']['emails']}**: {', '.join(EMAILS)}")
