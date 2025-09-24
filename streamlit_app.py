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
    {"id":"learning_sup",  "ar":"دعم تعليمي وصعوبات تعلم",   "en":"Learning support",        "mins":45, "price":300},
    {"id":"speech",        "ar":"جلسة نطق وتخاطب",           "en":"Speech & language",       "mins":45, "price":300},
]

# =========================
# Language (AR default)
# =========================
if "lang" not in st.session_state:
    st.session_state.lang = "ar"

lang = st.segmented_control("اللغة / Language", options=["ar","en"], default="ar", label_visibility="collapsed")
st.session_state.lang = lang

T = {
  "ar": {
    "title": f"🧠 {CLINIC_NAME} - مساعد ذكي (عرض تجريبي)",
    "subtitle": "واجهة عربية فقط. هذا ديمو للتجربة وليس نظاما نهائيا.",
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
    "title": f"🧠 {CLINIC_NAME} — Smart Assistant (Demo)",
    "subtitle": "Arabic-first demo. Not a final system.",
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
    "confirming": "Confirming",
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
    # Sunday=6; our WORK_DAYS includes Sun–Thu
    return d.weekday() in WORK_DAYS

def valid_phone(p: str) -> bool:
    if not p: return False
    p = p.strip().replace(" ", "")
    return bool(re.match(r"^(\+971|0)\d{8,9}$", p))

def gen_slots(d: date, duration_minutes: int):
    if not is_workday(d):
        return []
    start_dt = datetime.combine(d, OPEN_T)
    end_dt = datetime.combine(d, CLOSE_T)
    step = timedelta(minutes=max(15, duration_minutes))  # coarse step
    slots = []
    cur = start_dt
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

def quick_answer(user_text: str, lang="ar") -> str:
    t = (user_text or "").strip()
    # Location
    if any(k in t for k in (["موقع","عنوان","وين","لوكيشن"] if lang=="ar" else ["where","address","location"])):
        if lang=="ar":
            return f"العنوان: {ADDRESS_AR}\n({ADDRESS_EN})\nرابط خرائط جوجل: {MAPS_URL}"
        else:
            return f"Address: {ADDRESS_EN}\n(AR: {ADDRESS_AR})\nGoogle Maps: {MAPS_URL}"
    # Contact
    if any(k in t for k in (["تواصل","رقم","واتساب","هاتف"] if lang=="ar" else ["phone","number","contact","whatsapp"])):
        if lang=="ar":
            return f"ارقام الهاتف: {', '.join(PHONES)}\nالبريد الالكتروني: {', '.join(EMAILS)}"
        else:
            return f"Phones: {', '.join(PHONES)}\nEmails: {', '.join(EMAILS)}"
    # Hours
    if any(k in t for k in (["ساعات","العمل","دوام"] if lang=="ar" else ["hours","opening","open"])):
        if lang=="ar":
            return f"ساعات العمل: الاحد - الخميس {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (الجمعة والسبت مغلق)"
        else:
            return f"Hours: Sun–Thu {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (Fri & Sat closed)"
    # Pricing (avoid matching 'كم' inside 'موقعكم' by tokenizing)
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
# Header
# =========================
st.title(T[lang]["title"])
st.caption(T[lang]["subtitle"])

# =========================
# Tabs
# =========================
tab_chat, tab_book, tab_info = st.tabs(T[lang]["tabs"])

# -------------------------
# TAB: Chat
# -------------------------
with tab_chat:
    st.markdown(f"**{T[lang]['faq']}**")
    chips = T[lang]["chips"]
    st.markdown('<div class="chips">' + "".join([f'<a href="?q={quote(c)}">{c}</a>' for c in chips]) + "</div>", unsafe_allow_html=True)

    # Quick autofill from query
    q = st.query_params.get("q", None)
    default_text = q if q else ""

    user = st.text_input(T[lang]["ask"], value=default_text, key="chat_in")
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button(T[lang]["send"], use_container_width=True):
            if user:
                st.write(f"**انت:** {user}" if lang=="ar" else f"**You:** {user}")
                st.success(quick_answer(user, lang=lang))
    with col2:
        # human handoff / request callback
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
    st.write(f"**{T[lang]['hours']}**: "
             + (f"الاحد - الخميس {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (الجمعة والسبت مغلق)"
                if lang=='ar' else
                f"Sun–Thu {OPEN_T.strftime('%H:%M')} - {CLOSE_T.strftime('%H:%M')} (Fri & Sat closed)"))
    st.write(f"**{T[lang]['address']}**: {ADDRESS_AR if lang=='ar' else ADDRESS_EN}")
    st.markdown(f"[{T[lang]['maps']}]({MAPS_URL})")
    st.write(f"**{T[lang]['phones']}**: {', '.join(PHONES)}")
    st.write(f"**{T[lang]['emails']}**: {', '.join(EMAILS)}")

    # Copy address + WhatsApp location + Call now
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button(T[lang]["copy"], use_container_width=True):
            st.markdown(f"""
            <script>
            navigator.clipboard.writeText("{(ADDRESS_AR if lang=='ar' else ADDRESS_EN).replace('"','\\"')}\\n{MAPS_URL}");
            </script>
            """, unsafe_allow_html=True)
            st.toast("تم النسخ" if lang=="ar" else "Copied")
    with colB:
        wa_text = f"{'لوكيشن Alef Centre' if lang=='ar' else 'Alef Centre location'}:\\n" \
                  f"{ADDRESS_AR if lang=='ar' else ADDRESS_EN}\\n{MAPS_URL}"
        st.link_button(T[lang]["whatsapp_loc"], "https://wa.me/?text=" + quote(wa_text), use_container_width=True)
    with colC:
        st.link_button(T[lang]["call_now"], "tel:+97143881169", use_container_width=True)

    st.caption(T[lang]["privacy"])

# -------------------------
# TAB: Booking
# -------------------------
with tab_book:
    st.subheader(T[lang]["booking_title"])

    # Step 1 — service
    svc_names = [s["ar"] if lang=="ar" else s["en"] for s in SERVICES]
    svc_choice = st.selectbox(T[lang]["svc"], options=["—"] + svc_names, index=0)

    # Derive duration
    chosen = None
    if svc_choice and svc_choice != "—":
        for s in SERVICES:
            if s["ar"] == svc_choice or s["en"] == svc_choice:
                chosen = s; break

    # Step 2 — date
    today = date.today()
    min_day = today + timedelta(days=0)
    picked_day = st.date_input(T[lang]["date"], value=min_day, min_value=min_day)

    # Step 3 — time slots
    slots = gen_slots(picked_day, chosen["mins"] if chosen else 30)
    slot_labels = [t.strftime("%H:%M") for t in slots]
    slot_choice = st.selectbox(T[lang]["time"], options=["—"] + slot_labels, index=0)

    # Step 4 — contact
    colx, coly = st.columns(2)
    with colx:
        name = st.text_input(T[lang]["name"])
    with coly:
        phone = st.text_input(T[lang]["phone"])
    notes = st.text_area(T[lang]["notes"])

    # Confirm
    if st.button(T[lang]["confirm"], type="primary"):
        # Validation
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

        # Build confirmation
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

        # ICS download
        title = f"{CLINIC_NAME} — {svc_choice}"
        desc  = f"Ref: {ref} | Phone: {phone}"
        ics = ics_bytes(title, chosen_time, chosen["mins"], ADDRESS_EN, desc)
        st.download_button(T[lang]["ics"], data=ics, file_name=f"{ref}.ics", mime="text/calendar")

        # WhatsApp share confirmation (client’s own chat)
        confirm_text = (f"تم حجز موعدك في {CLINIC_NAME}.\n"
                        f"الخدمة: {svc_choice}\n"
                        f"التاريخ: {picked_day} - الوقت: {slot_choice}\n"
                        f"المرجع: {ref}\n"
                        f"العنوان: {ADDRESS_AR}\n{MAPS_URL}") if lang=="ar" else \
                       (f"Your appointment at {CLINIC_NAME} is booked.\n"
                        f"Service: {svc_choice}\n"
                        f"Date: {picked_day} - Time: {slot_choice}\n"
                        f"Ref: {ref}\n"
                        f"Address: {ADDRESS_EN}\n{MAPS_URL}")
        st.link_button("مشاركة التاكيد في واتساب" if lang=="ar" else "Share confirmation on WhatsApp",
                       "https://wa.me/?text=" + quote(confirm_text))

# -------------------------
# TAB: Info
# -------------------------
with tab_info:
    st.subheader(T[lang]["quick_info"])
    st.write(f"**{T[lang]['address']}**: {ADDRESS_AR if lang=='ar' else ADDRESS_EN}")
    st.markdown(f"[{T[lang]['maps']}]({MAPS_URL})")
    st.write(f"**{T[lang]['phones']}**: {', '.join(PHONES)}")
    st.write(f"**{T[lang]['emails']}**: {', '.join(EMAILS)}")

    st.markdown("---")
    st.subheader(T[lang]["what_do"])
    for b in T[lang]["what_do_bullets"]:
        st.write(f"- {b}")
    st.caption(T[lang]["privacy"])
