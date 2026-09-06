import base64
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================================================
#  Animo Bakery & Cafe — Digital Membership Card
#  Monthly-visit tier system: New / Featured / Premium
# =========================================================

st.set_page_config(page_title="Animo | بطاقة العضوية", page_icon="☕", layout="centered")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(APP_DIR, "animo_customers.csv")
LOGO_FILE = os.path.join(APP_DIR, "logo.jpeg")

CASHIER_PIN = "1234"        # رمز دخول لوحة الكاشير
NEW_CUSTOMER_PIN = "1427"   # رمز خاص إضافي لتسجيل عميل جديد
MAX_VISITS = 10             # الحد الأقصى للزيارات المحسوبة خلال الشهر

# الفئات مرتبة من الأعلى إلى الأقل — عدّل الأرقام هنا وقت ما تبين
TIERS = [
    {"key": "premium",  "name": "بريميوم", "name_en": "PREMIUM",  "visits": 10, "discount": 40, "color": "#C9A05C", "text": "#3A2E17"},
    {"key": "featured", "name": "مميز",     "name_en": "FEATURED", "visits": 6,  "discount": 25, "color": "#3B5336", "text": "#FAF6F0"},
    {"key": "new",      "name": "جديد",     "name_en": "NEW",      "visits": 3,  "discount": 10, "color": "#B7A88F", "text": "#2C221E"},
]
TIERS_ASC = sorted(TIERS, key=lambda t: t["visits"])

COLUMNS = ["Name", "Phone", "MonthlyVisits", "VisitMonth"]


# ---------------------------------------------------------
# Data layer
# ---------------------------------------------------------
def current_month_key() -> str:
    return datetime.now().strftime("%Y-%m")


def load_data() -> pd.DataFrame:
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype=str)
        except Exception:
            st.error("تعذّرت قراءة ملف البيانات، تم إنشاء قاعدة بيانات جديدة.")
            return pd.DataFrame(columns=COLUMNS)
        if "Name" not in df.columns:
            df["Name"] = ""
        if "Phone" not in df.columns:
            df["Phone"] = ""
        if "MonthlyVisits" not in df.columns:
            df["MonthlyVisits"] = 0
        if "VisitMonth" not in df.columns:
            df["VisitMonth"] = ""  # عملاء من نظام قديم يبدؤون بدون زيارات هذا الشهر
        df["Phone"] = df["Phone"].astype(str).str.strip()
        df["MonthlyVisits"] = pd.to_numeric(df["MonthlyVisits"], errors="coerce").fillna(0).astype(int)
        df["VisitMonth"] = df["VisitMonth"].astype(str)
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save_data(df: pd.DataFrame) -> bool:
    try:
        df.to_csv(DB_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"تعذّر حفظ البيانات: {e}")
        return False


def clean_phone(phone_str: str) -> str:
    digits = "".join(filter(str.isdigit, str(phone_str)))
    return digits.lstrip("0")


def find_customer_index(df: pd.DataFrame, phone: str) -> int:
    cleaned = clean_phone(phone)
    if not cleaned:
        return -1
    mask = df["Phone"].apply(lambda p: clean_phone(p) == cleaned)
    matches = df[mask]
    return matches.index[0] if len(matches) else -1


def effective_visits(row) -> int:
    """Visits that count toward THIS month; visits from a previous month don't carry over."""
    if str(row["VisitMonth"]) != current_month_key():
        return 0
    return int(row["MonthlyVisits"])


def get_tier(visits: int):
    for t in TIERS:  # already sorted highest-first
        if visits >= t["visits"]:
            return t
    return None


def get_next_tier(visits: int):
    for t in TIERS_ASC:
        if visits < t["visits"]:
            return t
    return None


def register_visit(df: pd.DataFrame, idx) -> tuple[int, bool]:
    """Adds one visit for the current month (auto-resets if the stored month has passed).
    Returns (new_visit_count, was_already_capped)."""
    month_now = current_month_key()
    if str(df.at[idx, "VisitMonth"]) != month_now:
        df.at[idx, "MonthlyVisits"] = 0
        df.at[idx, "VisitMonth"] = month_now
    current = int(df.at[idx, "MonthlyVisits"])
    if current >= MAX_VISITS:
        return current, True
    new_val = current + 1
    df.at[idx, "MonthlyVisits"] = new_val
    return new_val, False


if "cashier_auth" not in st.session_state:
    st.session_state.cashier_auth = False
if "new_customer_auth" not in st.session_state:
    st.session_state.new_customer_auth = False

df = load_data()

# ---------------------------------------------------------
# Styling — warm French-café identity (cream / deep green / gold)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Playfair+Display:ital,wght@0,600;1,500&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top, #FFFDFB 0%, #F6EFE6 55%, #F0E6D8 100%);
        color: #2C221E;
        direction: rtl;
    }

    .block-container { max-width: 560px; padding-top: 1.5rem; }

    .logo-container { display: flex; justify-content: center; align-items: center; margin-bottom: 10px; }
    .logo-img {
        width: 120px; height: 120px; border-radius: 50%; object-fit: cover;
        border: 3px solid #223322; box-shadow: 0 8px 20px rgba(34, 51, 34, 0.15);
    }

    .brand-name {
        text-align: center; font-family: 'Playfair Display', serif; font-weight: 700;
        font-style: italic; font-size: 34px; color: #223322; margin-bottom: 0;
    }
    .brand-subtitle {
        font-size: 12px; color: #7A6B5E; letter-spacing: 5px; margin-top: 4px;
        text-transform: uppercase; text-align: center; margin-bottom: 18px; font-weight: 600;
    }
    .divider {
        height: 1px; background: linear-gradient(90deg, transparent, #D4C5B9, transparent);
        margin: 6px 0 22px 0; border: none;
    }

    .card-container {
        background: linear-gradient(160deg, #FFFFFF 0%, #FBF5EE 100%);
        color: #2C221E; padding: 34px 26px; border-radius: 28px;
        box-shadow: 0 18px 45px rgba(44, 34, 30, 0.10);
        border: 1px solid #EADFD1; text-align: center; margin-top: 22px;
        position: relative; overflow: hidden;
    }
    .card-container::before {
        content: ""; position: absolute; top: 0; right: 0; left: 0; height: 6px;
        background: linear-gradient(90deg, #3B5336, #C9A05C, #3B5336);
    }
    .card-welcome {
        font-size: 13px; color: #8C7B6E; margin-bottom: 6px;
        text-transform: uppercase; letter-spacing: 2px; font-weight: 600;
    }
    .card-title {
        font-family: 'Playfair Display', serif; font-size: 26px; font-weight: 700;
        color: #223322; margin-bottom: 2px;
    }
    .card-subtitle { font-size: 11px; color: #9C8B7E; letter-spacing: 3px; margin-bottom: 20px; }

    .tier-badge {
        display: inline-block; padding: 8px 26px; border-radius: 30px;
        font-weight: 800; font-size: 17px; letter-spacing: 1px; margin: 6px 0 4px 0;
        box-shadow: 0 6px 14px rgba(0,0,0,0.12);
    }
    .tier-badge-en { font-size: 10px; letter-spacing: 3px; color: #9C8B7E; margin-bottom: 18px; }
    .discount-line { font-size: 15px; font-weight: 700; color: #3B5336; margin: 10px 0 20px 0; }
    .discount-line b { font-size: 22px; color: #223322; }

    .progress-wrap { margin: 10px 0 6px 0; }
    .progress-label { font-size: 12px; color: #8C7B6E; margin-bottom: 6px; font-weight: 600; }
    .progress-track {
        background-color: #F0E7DA; border-radius: 20px; height: 14px; overflow: hidden;
        border: 1px solid #E1D3C2;
    }
    .progress-fill {
        background: linear-gradient(90deg, #3B5336, #6B8E5A); height: 100%; border-radius: 20px;
    }
    .next-tier-note { font-size: 12px; color: #6B5C4F; margin-top: 12px; }
    .next-tier-note b { color: #3B5336; }

    .stTextInput label, .stSelectbox label { color: #223322 !important; font-weight: 700 !important; font-size: 15px !important; }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important; border: 1.5px solid #C9B8A5 !important;
        border-radius: 12px !important; color: #2C221E !important; font-weight: 600 !important;
    }
    input[inputmode="numeric"], input[type="tel"] { direction: ltr; text-align: right; }

    .stButton button {
        background-color: #223322 !important; color: #FAF6F0 !important; border-radius: 12px !important;
        border: none !important; font-weight: 700 !important; padding: 0.6rem 1.2rem !important;
        box-shadow: 0 6px 16px rgba(34, 51, 34, 0.25); transition: all .15s ease;
    }
    .stButton button:hover { background-color: #3B5336 !important; transform: translateY(-1px); }

    .cashier-badge {
        display: inline-block; background-color: #223322; color: #FAF6F0; font-size: 12px;
        font-weight: 700; padding: 4px 14px; border-radius: 20px; margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Header & Logo
# ---------------------------------------------------------
st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
if os.path.exists(LOGO_FILE):
    with open(LOGO_FILE, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()
    st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="logo-img">', unsafe_allow_html=True)
else:
    st.markdown("<div class='brand-name'>Animo</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='brand-subtitle'>Experience The Taste of France</div>", unsafe_allow_html=True)
st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar — cashier login (hidden from regular customers)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔐 لوحة التحكم الخاصة بالكاشير")
    st.markdown("---")

    if not st.session_state.cashier_auth:
        pass_input = st.text_input("رمز مرور الكاشير", type="password", placeholder="••••")
        if st.button("تسجيل دخول الكاشير", use_container_width=True):
            if pass_input.strip() == CASHIER_PIN:
                st.session_state.cashier_auth = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
    else:
        st.success("تم تسجيل الدخول بنجاح")
        if st.button("تسجيل خروج الكاشير", use_container_width=True):
            st.session_state.cashier_auth = False
            st.session_state.new_customer_auth = False
            st.rerun()

# ---------------------------------------------------------
# Customer view (main interface)
# ---------------------------------------------------------
if not st.session_state.cashier_auth:
    st.markdown(
        "<h4 style='color:#223322; text-align:center; font-family:Playfair Display, serif;'>استعرض بطاقة العضوية الخاصة بك</h4>",
        unsafe_allow_html=True,
    )
    customer_phone = st.text_input("رقم الجوال", placeholder="05xxxxxxxx")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_btn = st.button("عرض البطاقة", use_container_width=True)

    if search_btn:
        if not customer_phone.strip():
            st.error("الرجاء إدخال رقم الجوال.")
        elif len(clean_phone(customer_phone)) < 8:
            st.error("رقم الجوال غير صحيح، تأكد من إدخاله بشكل كامل.")
        else:
            idx = find_customer_index(df, customer_phone)
            if idx == -1:
                st.warning("رقم الجوال غير مسجل. يرجى الطلب من الكاشير تسجيلك في البرنامج أول مرة.")
            else:
                cust = df.loc[idx]
                visits = effective_visits(cust)
                tier = get_tier(visits)
                next_tier = get_next_tier(visits)
                progress_pct = min(int(visits / MAX_VISITS * 100), 100)

                if tier:
                    badge_html = (
                        f"<div class='tier-badge' style='background:{tier['color']}; color:{tier['text']};'>{tier['name']}</div>"
                        f"<div class='tier-badge-en'>{tier['name_en']} MEMBER</div>"
                        f"<div class='discount-line'>نسبة الخصم الحالية: <b>{tier['discount']}%</b></div>"
                    )
                else:
                    badge_html = (
                        "<div class='tier-badge' style='background:#F0E7DA; color:#8C7B6E; box-shadow:none; border:1px dashed #D9C9B7;'>ابدأ رحلتك</div>"
                        "<div class='tier-badge-en'>NO TIER YET</div>"
                        "<div class='discount-line'>أكمل زياراتك لتفتح أول خصم لك</div>"
                    )

                if next_tier:
                    remaining = next_tier["visits"] - visits
                    next_note = f"<div class='next-tier-note'>بقي لك <b>{remaining}</b> زيارات للوصول لفئة <b>{next_tier['name']}</b> وخصم <b>{next_tier['discount']}%</b></div>"
                else:
                    next_note = "<div class='next-tier-note'>🎉 وصلت لأعلى فئة هذا الشهر! استمتع بخصم البريميوم</div>"

                card_html = (
                    "<div class='card-container'>"
                    f"<div class='card-welcome'>Welcome, {cust['Name']}</div>"
                    "<div class='card-title'>بطاقة العضوية الرقمية</div>"
                    "<div class='card-subtitle'>DIGITAL MEMBERSHIP CARD</div>"
                    f"{badge_html}"
                    "<div class='progress-wrap'>"
                    f"<div class='progress-label'>زياراتك هذا الشهر: {visits} من {MAX_VISITS}</div>"
                    f"<div class='progress-track'><div class='progress-fill' style='width:{progress_pct}%;'></div></div>"
                    "</div>"
                    f"{next_note}"
                    "</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

                if tier and tier["key"] == "premium":
                    st.balloons()

# ---------------------------------------------------------
# Cashier panel (visible only when logged in via sidebar)
# ---------------------------------------------------------
else:
    st.markdown("<span class='cashier-badge'>لوحة تحكم الكاشير النشطة</span>", unsafe_allow_html=True)

    admin_action = st.selectbox(
        "الإجراء:", ["تسجيل عميل جديد", "تسجيل زيارة للعميل", "عرض كافة العملاء"]
    )

    # -- Register new customer (requires a second, separate PIN) --
    if admin_action == "تسجيل عميل جديد":
        if not st.session_state.new_customer_auth:
            st.info("تسجيل عميل جديد يتطلب رمزًا خاصًا إضافيًا.")
            extra_pin = st.text_input("الرمز الخاص", type="password", placeholder="••••", key="extra_pin_input")
            if st.button("تأكيد الرمز", use_container_width=True):
                if extra_pin.strip() == NEW_CUSTOMER_PIN:
                    st.session_state.new_customer_auth = True
                    st.rerun()
                else:
                    st.error("الرمز الخاص غير صحيح!")
        else:
            with st.form("new_cust", clear_on_submit=True):
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الجوال")
                submitted = st.form_submit_button("حفظ وتسجيل العميل")
                if submitted:
                    if not name.strip() or not phone.strip():
                        st.error("املأ كافة الحقول.")
                    elif len(clean_phone(phone)) < 8:
                        st.error("رقم الجوال غير صحيح.")
                    elif find_customer_index(df, phone) != -1:
                        st.warning("هذا الرقم مسجل مسبقاً.")
                    else:
                        new_row = {
                            "Name": name.strip(),
                            "Phone": phone.strip(),
                            "MonthlyVisits": 0,
                            "VisitMonth": current_month_key(),
                        }
                        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                        if save_data(df):
                            st.success(f"تم تسجيل العميل {name} بنجاح!")

    # -- Register a visit --
    elif admin_action == "تسجيل زيارة للعميل":
        if df.empty:
            st.info("لا يوجد عملاء مسجلين.")
        else:
            options = [f"{row.Name} — {row.Phone}" for row in df.itertuples()]
            sel = st.selectbox("اختر العميل", options)
            sel_idx = options.index(sel)
            cust_row = df.iloc[sel_idx]
            visits_now = effective_visits(cust_row)
            tier_now = get_tier(visits_now)
            tier_label = tier_now["name"] if tier_now else "بدون فئة بعد"
            st.write(f"**العميل:** {cust_row['Name']} | **زياراته هذا الشهر:** {visits_now}/{MAX_VISITS} | **الفئة:** {tier_label}")

            if st.button("➕ تسجيل زيارة جديدة", use_container_width=True):
                new_count, was_capped = register_visit(df, sel_idx)
                if was_capped:
                    st.info("العميل وصل بالفعل للحد الأقصى (10 زيارات) وحصل على خصم البريميوم لهذا الشهر.")
                else:
                    if save_data(df):
                        new_tier = get_tier(new_count)
                        if new_tier and (get_tier(new_count - 1) != new_tier):
                            st.balloons()
                            st.success(f"🎉 وصل العميل لفئة {new_tier['name']} وخصم {new_tier['discount']}%!")
                        else:
                            st.success(f"تم تسجيل الزيارة بنجاح! الإجمالي هذا الشهر: {new_count}/{MAX_VISITS}")

    # -- View all customers --
    elif admin_action == "عرض كافة العملاء":
        if df.empty:
            st.info("لا توجد بيانات.")
        else:
            view_df = df.copy()
            view_df["الزيارات هذا الشهر"] = view_df.apply(effective_visits, axis=1)
            view_df["الفئة"] = view_df["الزيارات هذا الشهر"].apply(lambda v: (get_tier(v) or {}).get("name", "بدون فئة"))
            view_df["الخصم"] = view_df["الزيارات هذا الشهر"].apply(lambda v: f"{(get_tier(v) or {}).get('discount', 0)}%")
            view_df = view_df.rename(columns={"Name": "الاسم", "Phone": "الجوال"})
            st.dataframe(
                view_df[["الاسم", "الجوال", "الزيارات هذا الشهر", "الفئة", "الخصم"]],
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"عدد العملاء المسجلين: {len(df)}  •  آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
