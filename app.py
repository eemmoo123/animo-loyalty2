import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================================================
#  Animo Bakery & Cafe — Digital Loyalty Card
# =========================================================

st.set_page_config(page_title="Animo | بطاقة الولاء", page_icon="☕", layout="centered")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(APP_DIR, "animo_customers.csv")
LOGO_FILE = os.path.join(APP_DIR, "logo.jpeg")
CASHIER_PIN = "1234"  # غيّر الرمز من هنا
TOTAL_STAMPS = 7

COLUMNS = ["Name", "Phone", "Punches", "FreeCoffeesEarned"]


# ---------------------------------------------------------
# Data layer
# ---------------------------------------------------------
def load_data() -> pd.DataFrame:
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype=str)
        except Exception:
            st.error("تعذّرت قراءة ملف البيانات، تم إنشاء قاعدة بيانات جديدة.")
            return pd.DataFrame(columns=COLUMNS)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = 0 if col in ("Punches", "FreeCoffeesEarned") else ""
        df["Phone"] = df["Phone"].astype(str).str.strip()
        df["Punches"] = pd.to_numeric(df["Punches"], errors="coerce").fillna(0).astype(int)
        df["FreeCoffeesEarned"] = pd.to_numeric(df["FreeCoffeesEarned"], errors="coerce").fillna(0).astype(int)
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


if "cashier_auth" not in st.session_state:
    st.session_state.cashier_auth = False

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

    /* ---------- Logo styling (Circular & Harmonious) ---------- */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 10px;
    }
    .logo-img {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #223322;
        box-shadow: 0 8px 20px rgba(34, 51, 34, 0.15);
    }

    /* ---------- Header ---------- */
    .brand-name {
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-style: italic;
        font-size: 34px;
        color: #223322;
        margin-bottom: 0;
    }
    .brand-subtitle {
        font-size: 12px;
        color: #7A6B5E;
        letter-spacing: 5px;
        margin-top: 4px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 18px;
        font-weight: 600;
    }
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #D4C5B9, transparent);
        margin: 6px 0 22px 0;
        border: none;
    }

    /* ---------- Loyalty card ---------- */
    .card-container {
        background: linear-gradient(160deg, #FFFFFF 0%, #FBF5EE 100%);
        color: #2C221E;
        padding: 36px 28px;
        border-radius: 28px;
        box-shadow: 0 18px 45px rgba(44, 34, 30, 0.10);
        border: 1px solid #EADFD1;
        text-align: center;
        margin-top: 22px;
        position: relative;
        overflow: hidden;
    }
    .card-container::before {
        content: "";
        position: absolute;
        top: 0; right: 0; left: 0;
        height: 6px;
        background: linear-gradient(90deg, #3B5336, #C9A05C, #3B5336);
    }
    .card-welcome {
        font-size: 13px;
        color: #8C7B6E;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
    }
    .card-title {
        font-family: 'Playfair Display', serif;
        font-size: 27px;
        font-weight: 700;
        color: #223322;
        margin-bottom: 2px;
    }
    .card-subtitle {
        font-size: 11px;
        color: #9C8B7E;
        letter-spacing: 3px;
        margin-bottom: 22px;
    }
    .rule-text {
        font-size: 16px;
        font-weight: 700;
        color: #3B5336;
        margin-bottom: 2px;
    }
    .rule-sub {
        font-size: 11px;
        color: #8C7B6E;
        margin-bottom: 22px;
        font-style: italic;
    }
    .stamp-row {
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 10px;
        margin: 18px 0;
    }
    .stamp-active {
        background: linear-gradient(135deg, #3B5336, #1B2A17);
        color: #FAF6F0;
        width: 44px; height: 44px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
        box-shadow: 0 4px 10px rgba(59, 83, 54, 0.30);
    }
    .stamp-inactive {
        background-color: #F3ECE1;
        border: 2px dashed #D9C9B7;
        color: #D9C9B7;
        width: 44px; height: 44px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
    }
    .footer-msg {
        font-size: 15px;
        font-weight: 700;
        color: #2C221E;
        margin-top: 18px;
    }
    .footer-note {
        font-size: 12px;
        color: #6B5C4F;
        margin-top: 10px;
    }
    .footer-note b { color: #3B5336; }

    /* ---------- Inputs & Labels Clarity Fixes ---------- */
    .stTextInput label, .stSelectbox label {
        color: #223322 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1.5px solid #C9B8A5 !important;
        border-radius: 12px !important;
        color: #2C221E !important;
        font-weight: 600 !important;
    }
    input[inputmode="numeric"], input[type="tel"] { direction: ltr; text-align: right; }
    
    /* ---------- Buttons Customization ---------- */
    .stButton button {
        background-color: #223322 !important;
        color: #FAF6F0 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 6px 16px rgba(34, 51, 34, 0.25);
        transition: all .15s ease;
    }
    .stButton button:hover {
        background-color: #3B5336 !important;
        transform: translateY(-1px);
    }
    .cashier-badge {
        display: inline-block;
        background-color: #223322;
        color: #FAF6F0;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 14px;
        border-radius: 20px;
        margin-bottom: 14px;
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
    # عرض اللوجو بشكل دائري ومتناسق
    import base64
    with open(LOGO_FILE, "rb") as img_file:
        encoded_img = base64.b64encode(img_file.read()).decode()
    st.markdown(f'<img src="data:image/jpeg;base64,{encoded_img}" class="logo-img">', unsafe_allow_html=True)
else:
    st.markdown("<div class='brand-name'>Animo</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='brand-subtitle'>Experience The Taste of France</div>", unsafe_allow_html=True)
st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar for Cashier (Hidden from regular customers)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🔐 لوحة التحكم الخاصة بالكاشير")
    st.markdown("---")
    
    if not st.session_state.cashier_auth:
        pass_input = st.text_input("رمز مرور الكاشير", type="password", placeholder="••••")
        if st.button("تسجيل دخول الكاشير", use_container_width=True):
            if pass_input == CASHIER_PIN:
                st.session_state.cashier_auth = True
                st.rerun()
            else:
                st.error("كلمة المرور غير صحيحة!")
    else:
        st.success("تم تسجيل الدخول بنجاح")
        if st.button("تسجيل خروج الكاشير", use_container_width=True):
            st.session_state.cashier_auth = False
            st.rerun()

# ---------------------------------------------------------
# Customer View (Main Interface)
# ---------------------------------------------------------
if not st.session_state.cashier_auth:
    st.markdown(
        "<h4 style='color:#223322; text-align:center; font-family:Playfair Display, serif;'>استعرض بطاقة الولاء الخاصة بك</h4>",
        unsafe_allow_html=True,
    )
    customer_phone = st.text_input(
        "رقم الجوال",
        placeholder="05xxxxxxxx",
    )

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
                punches = int(cust["Punches"])
                free_earned = int(cust["FreeCoffeesEarned"])
                remaining = max(TOTAL_STAMPS - punches, 0)

                stamps_html = "".join(
                    f"<div class='stamp-active'>☕</div>" if i <= punches else "<div class='stamp-inactive'>☕</div>"
                    for i in range(1, TOTAL_STAMPS + 1)
                )

                footer = (
                    f"بقي لك {remaining} أختام فقط لكوبك المجاني"
                    if remaining > 0
                    else "🎉 مبروك! استحقيت كوباً مجانياً الآن!"
                )

                card_html = (
                    "<div class='card-container'>"
                    f"<div class='card-welcome'>Welcome, {cust['Name']}</div>"
                    "<div class='card-title'>بطاقة الولاء الرقمية</div>"
                    "<div class='card-subtitle'>DIGITAL LOYALTY CARD</div>"
                    "<div class='rule-text'>سبعة أختام، والكوب الثامن علينا</div>"
                    "<div class='rule-sub'>Seven stamps. Eighth cup, on us.</div>"
                    f"<div class='stamp-row'>{stamps_html}</div>"
                    f"<div class='footer-msg'>{footer}</div>"
                    f"<div class='footer-note'>الأكواب المجانية المكتسبة: <b>{free_earned}</b></div>"
                    "</div>"
                )
                st.markdown(card_html, unsafe_allow_html=True)

                if punches >= TOTAL_STAMPS:
                    st.balloons()

# ---------------------------------------------------------
# Cashier Panel (Visible only when logged in via sidebar)
# ---------------------------------------------------------
else:
    st.markdown("<span class='cashier-badge'>لوحة تحكم الكاشير النشطة</span>", unsafe_allow_html=True)

    admin_action = st.selectbox(
        "الإجراء:", ["تسجيل عميل جديد", "إضافة ختم للعميل", "عرض كافة العملاء"]
    )

    # -- Register new customer --
    if admin_action == "تسجيل عميل جديد":
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
                        "Punches": 0,
                        "FreeCoffeesEarned": 0,
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_data(df):
                        st.success(f"تم تسجيل العميل {name} بنجاح!")

    # -- Add stamp --
    elif admin_action == "إضافة ختم للعميل":
        if df.empty:
            st.info("لا يوجد عملاء مسجلين.")
        else:
            options = [f"{row.Name} — {row.Phone}" for row in df.itertuples()]
            sel = st.selectbox("اختر العميل", options)
            sel_idx = options.index(sel)
            cust_row = df.iloc[sel_idx]
            st.write(f"**العميل:** {cust_row['Name']} | **الأختام الحالية:** {cust_row['Punches']}/{TOTAL_STAMPS}")

            if st.button("➕ إضافة ختم جديد", use_container_width=True):
                current = int(df.at[sel_idx, "Punches"]) + 1
                if current >= TOTAL_STAMPS:
                    df.at[sel_idx, "Punches"] = 0
                    df.at[sel_idx, "FreeCoffeesEarned"] = int(df.at[sel_idx, "FreeCoffeesEarned"]) + 1
                    if save_data(df):
                        st.balloons()
                        st.success("🎉 أكمل العميل 7 أختام واستحق الكوب المجاني!")
                else:
                    df.at[sel_idx, "Punches"] = current
                    if save_data(df):
                        st.success(f"تم إضافة الختم بنجاح! الإجمالي الآن: {current}/{TOTAL_STAMPS}")

    # -- View all customers --
    elif admin_action == "عرض كافة العملاء":
        if df.empty:
            st.info("لا توجد بيانات.")
        else:
            st.dataframe(
                df.rename(
                    columns={
                        "Name": "الاسم",
                        "Phone": "الجوال",
                        "Punches": "الأختام",
                        "FreeCoffeesEarned": "الأكواب المجانية",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"عدد العملاء المسجلين: {len(df)}  •  آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
