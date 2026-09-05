import streamlit as st
import pandas as pd
import os

# Page configuration
st.set_page_config(page_title="Animo Loyalty Card", page_icon="☕", layout="centered")

DB_FILE = "animo_customers.csv"
CASHIER_PIN = "1234"  # رمز مرور الكاشير

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # ضمان قراءة أرقام الجوال كنصوص دائماً لتجنب مشاكل التنسيق
        df["Phone"] = df["Phone"].astype(str).str.strip()
        return df
    else:
        return pd.DataFrame(columns=["Name", "Phone", "Punches", "FreeCoffeesEarned"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def clean_phone(phone_str):
    # إزالة أي مسافات أو رموز غير صالحة وتوحيد تنسيق الرقم
    phone = "".join(filter(str.isdigit, str(phone_str)))
    # إزالة الصفر البادئ إن وجد للمقارنة المرنة، أو التعامل معه بثبات
    return phone.lstrip('0')

df = load_data()

st.title("☕ Animo Coffee - Digital Loyalty Card")
st.markdown("نظام ولاء مقهى أنيمو: **كل 7 أكواب قهوة، الكوب الثامن مجاناً!**")

mode = st.radio("اختر واجهة الاستخدام:", ["🪪 بطاقة العميل (استعراض الأختام)", "👨‍🍳 لوحة الكاشير (محمية بكلمة مرور)"])

if mode == "🪪 بطاقة العميل (استعراض الأختام)":
    st.subheader("أهلاً بك! أدخل رقم جوالك لاستعراض بطاقتك")
    customer_phone = st.text_input("رقم الجوال (مثال: 05xxxxxxxx أو الرقم مباشرة)")
    
    if st.button("عرض البطاقة"):
        if customer_phone:
            cleaned_input = clean_phone(customer_phone)
            
            # البحث بمرونة بغض النظر عن وجود الصفر من عدمه
            matched_idx = -1
            for idx, row in df.iterrows():
                if clean_phone(row["Phone"]) == cleaned_input:
                    matched_idx = idx
                    break
            
            if matched_idx != -1:
                cust = df.iloc[matched_idx]
                st.success(f"مرحباً بك يا {cust['Name']}!")
                
                st.markdown("---")
                st.subheader("🎫 بطاقة الولاء الخاصة بك")
                st.write(f"**عدد الأختام الحالية:** {cust['Punches']} من 7")
                
                progress = min(int(cust['Punches']) / 7.0, 1.0)
                st.progress(progress)
                
                if int(cust['Punches']) < 7:
                    st.info(f"متبقي لك {7 - int(cust['Punches'])} أكواب لتصل إلى الكوب المجاني!")
                else:
                    st.balloons()
                    st.success("🎉 مبروك! لقد أكملت 7 أكواب ولديك كوب قهوة مجاني مستحق!")
                
                st.write(f"🎁 **الأكواب المجانية المكتسبة حتى الآن:** {cust['FreeCoffeesEarned']}")
                st.markdown("---")
            else:
                st.warning("رقم الجوال غير مسجل. يرجى الطلب من الكاشير تسجيلك في البرنامج أول مرة.")
        else:
            st.error("الرجاء إدخال رقم الجوال.")

else:
    st.subheader("تسجيل دخول الكاشير")
    pass_input = st.text_input("أدخل رمز المرور الخاص بالكاشير", type="password")
    
    if pass_input == CASHIER_PIN:
        st.success("تم تسجيل الدخول بنجاح للمنطقة الإدارية.")
        admin_action = st.selectbox("الإجراء:", ["تسجيل عميل جديد", "إضافة ختم للعميل", "عرض كافة العملاء"])
        
        if admin_action == "تسجيل عميل جديد":
            with st.form("new_cust"):
                name = st.text_input("اسم العميل")
                phone = st.text_input("رقم الجوال")
                submitted = st.form_submit_button("حفظ وتسجيل")
                if submitted:
                    if name and phone:
                        cleaned_new_phone = clean_phone(phone)
                        # التحقق هل الرقم موجود مسبقاً بطريقة مرنة
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
                        st.success("🎉 أكمل العميل 7 أكواب واستحق الكوب المجاني!")
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
