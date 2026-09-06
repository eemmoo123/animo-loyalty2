import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================================================
#  Animo Bakery & Cafe — Advanced Tiered Loyalty Program
# =========================================================

st.set_page_config(page_title="Animo | برنامج الولاء", page_icon="☕", layout="centered")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(APP_DIR, "animo_customers_tiered.csv")
LOGO_FILE = os.path.join(APP_DIR, "logo.jpeg")
CASHIER_PIN = "1234"  # رمز دخول الكاشير

# قواعد المستويات الشهرية (الحد الأقصى 10 زيارات بشهر)
MAX_MONTHLY_VISITS = 10
TIER_THRESHOLDS = {
    "بريميوم (Premium)": {"min_visits": 10, "discount": "40%"},
    "مميز (VIP)": {"min_visits": 6, "discount": "20%"},
    "جديد / عادي (New)": {"min_visits": 1, "discount": "10%"},
}

COLUMNS = ["Name", "Phone", "Visits", "LastMonth", "FreeCoffeesEarned"]


# ---------------------------------------------------------
# Data layer & Monthly Reset Logic
# ---------------------------------------------------------
def load_data() -> pd.DataFrame:
    current_month = datetime.now().strftime("%Y-%m")
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE, dtype=str)
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
        
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = "0" if col in ("Visits", "FreeCoffeesEarned") else current_month
                
        df["Phone"] = df["Phone"].astype(str).str.strip()
        df["Visits"] = pd.to_numeric(df["Visits"], errors="coerce").fillna(0).astype(int)
        df["FreeCoffeesEarned"] = pd.to_numeric(df["FreeCoffeesEarned"], errors="coerce").fillna(0).astype(int)
        
        # شرط تصفير الزيارات تلقائياً إذا دخلنا شهراً جديداً ولم يكمل العميل
        for idx, row in df.iterrows():
            last_m = str(row.get("LastMonth", current_month))
            if last_m != current_month:
                df.at[idx, "Visits"] = 0
                df.at[idx, "LastMonth"] = current_month
        save_data(df)
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


def get_customer_tier(visits: int):
    if visits >= 10:
        return "بريميوم (Premium)", "40%", "#C9A05C", "👑"
    elif visits >= 6:
        return "مميز (VIP)", "20%", "#3B5336", "⭐"
    elif visits >= 1:
        return "جديد (New)", "10%", "#8C7B6E", "☕"
    else:
        return "بدون زيارات شهرية", "0%", "#A38F7D", "⚪"


if "cashier_auth" not in st.session_state:
    st.session_state.cashier_auth = False

df = load_data()

# ---------------------------------------------------------
# Styling — French Café Identity
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

    /* إصلاح مشكلة الخط الوهمي عند إغلاق/طي السايدبار */
    section[data-testid="stSidebar"] {
        background-color: #223322;
        color: #FAF6F0;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: -1rem;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] div[data-testid="stSidebarContent"] {
        display: none;
    }

    /* ---------- Logo Styling ---------- */
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

    /* ---------- Tier Card Design ---------- */
    .tier-card {
        background: linear-gradient(160deg, #FFFFFF 0%, #FBF5EE 100%);
        color: #2C221E;
        padding: 30px 24px;
        border-radius: 28px;
        box-shadow: 0 18px 45px rgba(44, 34, 30, 0.10);
        border: 1px solid #EADFD1;
        text-align: center;
        margin-top: 22px;
        position: relative;
        overflow: hidden;
    }
    .tier-card::before {
        content: "";
        position: absolute;
        top: 0; right: 0; left: 0;
        height: 6px;
        background: linear-gradient(90deg, #3B5336, #C9A05C, #3B5336);
    }
    .tier-title {
        font-family: 'Playfair Display', serif;
        font-size: 24px;
        font-weight: 700;
        color: #223322;
        margin-bottom: 8px;
    }
    .badge-box {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 15px;
        color: #FFF;
        margin: 10px 0;
    }
    
    /* ---------- Inputs & Labels ---------- */
    section[data-testid="stSidebar"] .stTextInput label {
        color: #FAF6F0 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }
    .block-container .stTextInput label, .block-container .stSelectbox label {
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
    
    /* ---------- Buttons & Form Submit Buttons Fix ---------- */
    .stButton button, 
    div[data-testid="stFormSubmitButton"] button {
        background-color: #223322 !important;
        color: #FAF6F0 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 6px 16px rgba(34, 51, 34, 0.25) !important;
        transition: all .15s ease !important;
    }
    .stButton button *, 
    div[data-testid="stFormSubmitButton"] button * {
        color: #FAF6F0 !important;
        font-weight: 700 !important;
    }
    .stButton button:hover, 
    div[data-testid="stFormSubmitButton"] button:hover {
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
# Sidebar for Cashier (Hidden & Protected)
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
        "<h4 style='color:#223322; text-align:center; font-family:Playfair Display, serif;'>استعلم عن مستواك الشهري وخصمك</h4>",
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
            st.error("رقم الجوال غير صحيح.")
        else:
            idx = find_customer_index(df, customer_phone)
            if idx == -1:
                st.warning("رقم الجوال غير مسجل. اطلب من الكاشير تسجيلك في البرنامج.")
            else:
                cust = df.loc[idx]
                visits = int(cust["Visits"])
                tier_name, discount, color, emoji = get_customer_tier(visits)
                remaining_to_max = max(MAX_MONTHLY_VISITS - visits, 0)

                # رسم التقدم الشهري (الأختام حتى 10)
                stamps_html = "".join(
                    f"<div style='background: {color}; color: #fff; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 3px 8px rgba(0,0,0,0.15);'>{i}</div>"
                    if i <= visits else 
                    f"<div style='background: #F3ECE1; border: 2px dashed #D9C9B7; color: #D9C9B7; width: 38px; height: 38px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;'>{i}</div>"
                    for i in range(1, MAX_MONTHLY_VISITS + 1)
                )

                card_html = f"""
                <div class='tier-card'>
                    <div style='font-size: 13px; color: #8C7B6E; letter-spacing: 2px; font-weight: 600;'>WELCOME, {cust['Name']}</div>
                    <div class='tier-title'>بطاقة الولاء الشهرية</div>
                    <div style='font-size: 11px; color: #9C8B7E; letter-spacing: 2px; margin-bottom: 12px;'>MONTHLY REWARDS PROGRAM</div>
                    
                    <div class='badge-box' style='background-color: {color};'>
                        {emoji} الفئة الحالية: {tier_name}
                    </div>
                    
                    <div style='font-size: 16px; font-weight: 700; color: #223322; margin: 10px 0;'>
                        نسبة الخصم الحالي: <span style='color: {color}; font-size: 20px;'>{discount}</span>
                    </div>
                    
                    <div style='font-size: 13px; color: #6B5C4F; margin-bottom: 15px;'>
                        عدد زياراتك هذا الشهر: <b>{visits} / {MAX_MONTHLY_VISITS}</b>
                    </div>
                    
                    <div style='display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; margin: 15px 0;'>
                        {stamps_html}
                    </div>
                    
                    <div style='font-size: 12px; color: #8C7B6E; margin-top: 15px; border-top: 1px solid #EADFD1; padding-top: 12px;'>
                        {f"باقي لك {remaining_to_max} زيارات لتصل لفئة <b>البريميوم (40%)</b>" if visits < 10 else "🎉 لقد وصلت للحد الأقصى واستحققت خصم 40% لهذا الشهر!"}
                    </div>
                    <div style='font-size: 10px; color: #A38F7D; margin-top: 6px; font-style: italic;'>
                        * تنبيه: يتم تصفير الزيارات تلقائياً مع بداية كل شهر ميلادي جديد.
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

                if visits >= 10:
                    st.balloons()

# ---------------------------------------------------------
# Cashier Panel (Visible only when logged in)
# ---------------------------------------------------------
else:
    st.markdown("<span class='cashier-badge'>لوحة تحكم الكاشير النشطة</span>", unsafe_allow_html=True)

    admin_action = st.selectbox(
        "الإجراء:", ["تسجيل عميل جديد", "تسجيل زيارة جديدة (ختم)", "عرض كافة العملاء والمستويات"]
    )

    # -- Register new customer --
    if admin_action == "تسجيل عميل جديد":
        with st.form("new_cust_tier", clear_on_submit=True):
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
                    current_month = datetime.now().strftime("%Y-%m")
                    new_row = {
                        "Name": name.strip(),
                        "Phone": phone.strip(),
                        "Visits": 0,
                        "LastMonth": current_month,
                        "FreeCoffeesEarned": 0,
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_data(df):
                        st.success(f"تم تسجيل العميل {name} بنجاح!")

    # -- Add visit / stamp --
    elif admin_action == "تسجيل زيارة جديدة (ختم)":
        if df.empty:
            st.info("لا يوجد عملاء مسجلين.")
        else:
            options = [f"{row.Name} — {row.Phone} (زيارات الشهر: {row.Visits})" for row in df.itertuples()]
            sel = st.selectbox("اختر العميل", options)
            sel_idx = options.index(sel)
            cust_row = df.iloc[sel_idx]
            
            t_name, t_disc, _, _ = get_customer_tier(int(cust_row['Visits']))
            st.info(f"العميل: **{cust_row['Name']}** | الفئة الحالية: **{t_name}** | الخصم: **{t_disc}**")

            if st.button("➕ تسجيل زيارة اليوم", use_container_width=True):
                current_visits = int(df.at[sel_idx, "Visits"]) + 1
                df.at[sel_idx, "Visits"] = current_visits
                df.at[sel_idx, "LastMonth"] = datetime.now().strftime("%Y-%m")
                
                if save_data(df):
                    new_t, new_d, _, _ = get_customer_tier(current_visits)
                    st.success(f"تم تسجيل الزيارة بنجاح! إجمالي زياراته هذا الشهر: {current_visits} | الفئة الجديدة: {new_t} (خصم {new_d})")
                    if current_visits >= 10:
                        st.balloons()

    # -- View all customers --
    elif admin_action == "عرض كافة العملاء والمستويات":
        if df.empty:
            st.info("لا توجد بيانات.")
        else:
            display_df = df.copy()
            display_df["Tier"] = display_df["Visits"].apply(lambda v: get_customer_tier(v)[0])
            display_df["Discount"] = display_df["Visits"].apply(lambda v: get_customer_tier(v)[1])
            
            st.dataframe(
                display_df.rename(
                    columns={
                        "Name": "الاسم",
                        "Phone": "الجوال",
                        "Visits": "زيارات الشهر",
                        "Tier": "فئة العميل",
                        "Discount": "نسبة الخصم",
                        "FreeCoffeesEarned": "المكافآت",
                    }
                )[["الاسم", "الجوال", "زيارات الشهر", "فئة العميل", "نسبة الخصم"]],
                use_container_width=True,
                hide_index=True,
            )
            st.caption(f"عدد العملاء المسجلين: {len(df)}  •  الشهر الحالي: {datetime.now().strftime('%Y-%m')}")
