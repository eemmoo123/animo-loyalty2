import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="Animo - Loyalty Card", page_icon="☕", layout="centered")

DB_FILE = "animo_customers.csv"
LOGO_FILE = "logo.jpeg"
CASHIER_PIN = "1234"  # رمز مرور الكاشير

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df["Phone"] = df["Phone"].astype(str).str.strip()
        return df
    else:
        return pd.DataFrame(columns=["Name", "Phone", "Punches", "FreeCoffeesEarned"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def clean_phone(phone_str):
    phone = "".join(filter(str.isdigit, str(phone_str)))
    return phone.lstrip('0')

df = load_data()

# Custom French-Café Bright & Luxury Styling (CSS)
st.markdown("""
    <style>
    .stApp {
        background-color: #FAF6F0;
        color: #2C221E;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #8C7B6E;
        letter-spacing: 4px;
        margin-top: 5px;
        text-transform: uppercase;
        text-align: center;
        margin-bottom: 20px;
    }
    .stRadio > label {
        color: #223322 !important;
        font-weight: 700 !important;
        font-size: 17px !important;
    }
    .stRadio div[role="radiogroup"] {
        background-color: #F0EAE1;
        padding: 10px 20px;
        border-radius: 14px;
        border: 1px solid #D4C5B9;
    }
    .stRadio div[role="radiogroup"] label p {
        color: #223322 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    .stTextInput label, .stSelectbox label {
        color: #2C221E !important;
        font-weight: 600 !important;
    }
    .card-container {
        background: linear-gradient(145deg, #FFFFFF, #F5EFEB);
        color: #2C221E;
        padding: 35px;
        border-radius: 24px;
        box-shadow: 0 12px 35px rgba(44, 34, 30, 0.08);
        border: 1px solid #E6DCD0;
        text-align: center;
        margin-top: 25px;
    }
    .card-title {
        font-size: 26px;
        font-weight: bold;
        color: #223322;
        margin-bottom: 2px;
        font-family: serif;
    }
    .card-subtitle {
        font-size: 12px;
        color: #9C8B7E;
        letter-spacing: 2px;
        margin-bottom: 25px;
    }
    .rule-text {
        font-size: 17px;
        font-weight: 700;
        color: #3B5336;
        margin-bottom: 2px;
    }
    .rule-sub {
        font-size: 11px;
        color: #9C8B7E;
        margin-bottom: 25px;
    }
    .stamp-active {
        background: linear-gradient(135deg, #3B5336, #223322);
        color: #FAF6F0;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        box-shadow: 0 4px 10px rgba(59, 83, 54, 0.25);
        margin: 0 4px;
    }
    .stamp-inactive {
        background-color: #F0EAE1;
        border: 2px dashed #D4C5B9;
        color: #D4C5B9;
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin: 0 4px;
    }
    .footer-msg {
        font-size: 15px;
        font-weight: 600;
        color: #2C221E;
        margin-top: 20px;
    }
    .stTextInput input, .stSelectbox select {
        background-color: #FFFFFF !important;
        border: 1px solid #D4C5B9 !important;
        border-radius: 12px !important;
        color: #2C221E !important;
    }
    .stButton button {
        background-color: #3B5336 !important;
        color: #FAF6F0 !important;
        border-radius: 12px !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 4px 12px rgba(59, 83, 54, 0.2);
    }
    .stButton button:hover {
        background-color: #223322 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Header Branding with Logo
col_l, col_m, col_r = st.columns([1, 1.2, 1])
with col_m:
    if os.path.exists(LOGO_FILE):
        st.image(LOGO_FILE, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #223322; font-family: serif;'>Animo Bakery & Cafe</h1>", unsafe_allow_html=True)

st.markdown("<div class='brand-subtitle'>Experience The Taste of France</div>", unsafe_allow_html=True)
st.markdown("---")

# Main Interface Switcher
mode = st.radio("اختر واجهة الاستخدام:", ["✨ بطاقة العميل الذكية", "🔐 لوحة تحكم الكاشير"], horizontal=True)
st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

if mode == "✨ بطاقة العميل الذكية":
    st.markdown("<h4 style='color: #223322; text-align: center; font-family: serif;'>استعرض بطاقة الولاء الخاصة بك</h4>", unsafe_allow_html=True)
    customer_phone = st.text_input("رقم الجوال (مثال: 05xxxxxxxx)", placeholder="أدخل رقم جوالك هنا...")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_btn = st.button("عرض البطاقة الفاخرة", use_container_width=True)
    
    if search_btn:
        if customer_phone:
            cleaned_input = clean_phone(customer_phone)
            matched_idx = -1
            for idx, row in df.iterrows():
                if clean_phone(row["Phone"]) == cleaned_input:
                    matched_idx = idx
                    break
            
            if matched_idx != -1:
                cust = df.iloc[matched_idx]
                punches = int(cust['Punches'])
                free_earned = int(cust['FreeCoffeesEarned'])
                remaining = 7 - punches
                
                # بناء الأختام بشكل مرئي مباشر لتجنب مشاكل العرض النصي
                stamps_html_parts = ""
                for i in range(1, 8):
                    if i <= punches:
                        stamps_html_parts += "<div class='stamp-active'>☕</div>"
                    else:
                        stamps_html_parts += "<div class='stamp-inactive'>☕</div>"

                st.markdown(f"""
                <div class='card-container'>
                    <div style='font-size: 13px; color: #8C7B6E; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;'>Welcome, {cust['Name']}</div>
                    <div class='card-title'>بطاقة الولاء الرقمية</div>
                    <div class='card-subtitle'>DIGITAL LOYALTY CARD</div>
                    
                    <div class='rule-text'>سبعة أختام، والكوب الثامن علينا</div>
                    <div class='rule-sub'>Seven stamps. Eighth cup, on us.</div>
                    
                    <div style='margin: 20px 0;'>
                        {stamps_html_parts}
                    </div>
                    
                    <div class='footer-msg'>
                        {"بقي لك " + str(remaining) + " أختام فقط لكوبك المجاني" if remaining > 0 else "🎉 مبروك! استحقيت كوباً مجانياً الآن!"}
                    </div>
                    <div style='font-size: 12px; color: #8C7B6E; margin-top: 12px;'>الأكواب المجانية المكتسبة: <b style='color: #3B5336;'>{free_earned}</b></div>
                </div>
                """, unsafe_allow_html=True)
                
                if punches >= 7:
                    st.balloons()
            else:
                st.warning("رقم الجوال غير مسجل. يرجى الطلب من الكاشير تسجيلك في البرنامج أول مرة.")
        else:
            st.error("الرجاء إدخال رقم الجوال.")

else:
    st.markdown("<h4 style='color: #223322; font-family: serif;'>تسجيل دخول الكاشير</h4>", unsafe_allow_html=True)
    pass_input = st.text_input("أدخل رمز المرور الخاص بالكاشير", type="password", placeholder="••••")
    
    if pass_input == CASHIER_PIN:
        st.success("تم تسجيل الدخول بنجاح للمنطقة الإدارية.")
        admin_action = st.selectbox("الإجراء:", ["تسجيل عميل جديد", "إضافة ختم للعميل", "عرض كافة العملاء"])
        
        if admin_action == "تسجيل عميل جديد":
            with st.form("new_cust"):
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الجوال")
                submitted = st.form_submit_button("حفظ وتسجيل العميل")
                if submitted:
                    if name and phone:
                        cleaned_new_phone = clean_phone(phone)
                        exists = any(clean_phone(p) == cleaned_new_phone for p in df["Phone"])
                        if exists:
                            st.warning("هذا الرقم مسجل مسبقاً.")
                        else:
                            new_row = {"Name": name, "Phone": phone.strip(), "Punches": 0, "FreeCoffeesEarned": 0}
                            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                            save_data(df)
                            st.success(f"تم تسجيل العميل {name} بنجاح!")
                    else:
                        st.error("املأ كافة الحقول.")
                        
        elif admin_action == "إضافة ختم للعميل":
            if df.empty:
                st.info("لا يوجد عملاء مسجلين.")
            else:
                phone_list = df["Phone"].tolist()
                sel_phone = st.selectbox("اختر رقم العميل", phone_list)
                cust_row = df[df["Phone"] == sel_phone].iloc[0]
                st.write(f"**العميل:** {cust_row['Name']} | **الأختام الحالية:** {cust_row['Punches']}/7")
                
                if st.button("➕ إضافة ختم جديد"):
                    idx = df[df["Phone"] == sel_phone].index[0]
                    current = int(df.at[idx, "Punches"]) + 1
                    if current >= 7:
                        df.at[idx, "Punches"] = 0
                        df.at[idx, "FreeCoffeesEarned"] = int(df.at[idx, "FreeCoffeesEarned"]) + 1
                        st.balloons()
                        st.success("🎉 أكمل العميل 7 أختام واستحق الكوب المجاني!")
                    else:
                        df.at[idx, "Punches"] = current
                        st.success(f"تم إضافة الختم بنجاح! الإجمالي الآن: {current}/7")
                    save_data(df)
                    
        elif admin_action == "عرض كافة العملاء":
            if df.empty:
                st.info("لا توجد بيانات.")
            else:
                st.dataframe(df, use_container_width=True)
                
    elif pass_input != "":
        st.error("كلمة المرور غير صحيحة!")
    else:
        st.info("الرجاء إدخال كلمة المرور للوصول إلى لوحة الكاشير.")
