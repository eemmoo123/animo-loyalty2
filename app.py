import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="Animo - Loyalty Card", page_icon="☕", layout="centered")

DB_FILE = "animo_customers.csv"
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

# Custom French-Café Styling (CSS)
st.markdown("""
    <style>
    .main {
        background-color: #12100e;
        color: #f7f2eb;
    }
    .stApp {
        background-color: #12100e;
    }
    .card-container {
        background-color: #f7f2eb;
        color: #2c221e;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        text-align: center;
        font-family: serif;
        margin-top: 20px;
    }
    .card-title {
        font-size: 28px;
        font-weight: bold;
        color: #2c221e;
        margin-bottom: 5px;
    }
    .card-subtitle {
        font-size: 14px;
        color: #7c6f64;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }
    .rule-text {
        font-size: 18px;
        font-weight: bold;
        color: #3b5336;
        margin-bottom: 5px;
    }
    .rule-sub {
        font-size: 12px;
        color: #8c7b6e;
        margin-bottom: 25px;
    }
    .stamps-grid {
        display: flex;
        justify-content: center;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 25px;
    }
    .stamp-circle {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
    }
    .stamp-active {
        background-color: #3b5336;
        color: #f7f2eb;
        box-shadow: 0 4px 10px rgba(59,83,54,0.3);
    }
    .stamp-inactive {
        background-color: #ede4d8;
        border: 2px dashed #bfaea0;
        color: #bfaea0;
    }
    .footer-msg {
        font-size: 16px;
        font-weight: bold;
        color: #2c221e;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Header Branding
st.markdown("<h1 style='text-align: center; color: #f7f2eb; font-family: serif;'>Animo Bakery & Cafe</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #bfaea0; letter-spacing: 3px;'>EXPERIENCE THE TASTE OF FRANCE</p>", unsafe_allow_html=True)

mode = st.radio("اختر واجهة الاستخدام:", ["🪪 بطاقة العميل (استعراض الأختام)", "👨‍🍳 لوحة الكاشير (محمية بكلمة مرور)"], horizontal=True)

if mode == "🪪 بطاقة العميل (استعراض الأختام)":
    st.markdown("### استعراض بطاقة الولاء الخاصة بك")
    customer_phone = st.text_input("أدخل رقم جوالك (مثال: 05xxxxxxxx)")
    
    if st.button("عرض البطاقة الفاخرة"):
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
                
                # بناء دوائر الأختام (7 أختام)
                stamps_html = "<div class='stamps-grid'>"
                for i in range(1, 8):
                    if i <= punches:
                        stamps_html += "<div class='stamp-circle stamp-active'>☕</div>"
                    else:
                        stamps_html += "<div class='stamp-circle stamp-inactive'>☕</div>"
                stamps_html += "</div>"
                
                # بطاقة العميل بتصميم فرنسي أنيق
                card_html = f"""
                <div class='card-container'>
                    <div style='font-size: 14px; color: #7c6f64; margin-bottom: 5px;'>مرحباً بك، {cust['Name']}</div>
                    <div class='card-title'>بطاقة الولاء</div>
                    <div class='card-subtitle'>LOYALTY CARD</div>
                    
                    <div class='rule-text'>سبعة أختام، والكوب الثامن علينا</div>
                    <div class='rule-sub'>Seven stamps. Eighth cup, on us.</div>
                    
                    {stamps_html}
                    
                    <div class='footer-msg'>
                        {f"بقي لك {remaining} أختام فقط لكوبك المجاني" if remaining > 0 else "🎉 مبروك! استحقيت كوباً مجانياً الآن!"}
                    </div>
                    <div style='font-size: 13px; color: #7c6f64; margin-top: 10px;'>الأكواب المجانية المكتسبة: {free_earned}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                if punches >= 7:
                    st.balloons()
            else:
                st.warning("رقم الجوال غير مسجل. يرجى الطلب من الكاشير تسجيلك في البرنامج أول مرة.")
        else:
            st.error("الرجاء إدخال رقم الجوال.")

else:
    st.markdown("### تسجيل دخول الكاشير")
    pass_input = st.text_input("أدخل رمز المرور الخاص بالكاشير", type="password")
    
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
