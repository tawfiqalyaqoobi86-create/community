import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection, init_db
from datetime import datetime, timedelta
import time
import os

# إعدادات الصفحة
st.set_page_config(page_title="مساعد مشرف تنمية العلاقات المجتمعية", layout="wide", initial_sidebar_state="expanded")

# تهيئة قاعدة البيانات
init_db()

# --- نظام إدارة الجلسة والمصادقة ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None

def add_log(action):
    conn = get_connection()
    conn.execute("INSERT INTO logs (user, action) VALUES (?, ?)", (st.session_state.username, action))
    conn.commit()
    conn.close()

def login():
    st.title("🔐 تسجيل الدخول للنظام")
    with st.form("login_form"):
        u = st.text_input("اسم المستخدم")
        p = st.text_input("كلمة المرور", type="password")
        if st.form_submit_button("دخول"):
            conn = get_connection()
            user = conn.execute("SELECT role FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            conn.close()
            if user:
                st.session_state.authenticated = True
                st.session_state.username = u
                st.session_state.user_role = user[0]
                add_log("قام بتسجيل الدخول")
                st.rerun()
            else:
                st.error("خطأ في بيانات الدخول")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- وظائف مساعدة ---
def load_data(table):
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# --- التنسيق البصري المخصص ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: RTL; text-align: right; }
    .stApp { background-color: #f8fafc; }
    section[data-testid="stSidebar"] { background-color: #1e293b !important; }
    section[data-testid="stSidebar"] * { color: white !important; }
    .stMetric { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    </style>
""", unsafe_allow_html=True)

# --- القائمة الجانبية ---
local_now = datetime.utcnow() + timedelta(hours=4)
st.sidebar.markdown(f"### 🕒 {local_now.strftime('%I:%M %p')}")
st.sidebar.info(f"👤 المستخدم: {st.session_state.username}\n\n🎖️ الصلاحية: {st.session_state.user_role}")

menu_options = ["📊 لوحة التحكم", "📅 خطة العمل", "👨‍👩‍👧‍👦 الشركاء", "🚀 المبادرات", "🎭 الفعاليات", "📈 التقارير", "🤖 الذكاء الاصطناعي", "⚙️ الإعدادات"]
menu = st.sidebar.radio("القائمة الرئيسية", menu_options)

if st.sidebar.button("🚪 تسجيل الخروج"):
    add_log("قام بتسجيل الخروج")
    st.session_state.authenticated = False
    st.rerun()

# --- منطق الصفحات ---

if menu == "📊 لوحة التحكم":
    st.title("📊 مركز القيادة")
    df_p = load_data("parents")
    df_i = load_data("initiatives")
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الشركاء", len(df_p))
    c2.metric("المبادرات الجارية", len(df_i[df_i['status'] != 'مكتملة']) if not df_i.empty else 0)
    c3.metric("معدل الأثر العام", f"{df_i['impact_score'].mean():.1f}" if not df_i.empty else "0.0")

elif menu == "⚙️ الإعدادات":
    st.title("⚙️ الإعدادات والصلاحيات")
    tab1, tab2, tab3, tab4 = st.tabs(["👥 إدارة المستخدمين", "🎨 تخصيص الواجهة", "💾 النسخ الاحتياطي", "📜 سجل النشاطات"])
    
    with tab1:
        if st.session_state.user_role == "مدير":
            st.subheader("إضافة مستخدم جديد")
            with st.form("new_user"):
                new_u = st.text_input("اسم المستخدم")
                new_p = st.text_input("كلمة المرور")
                new_r = st.selectbox("الصلاحية", ["مستخدم", "مدير"])
                if st.form_submit_button("إضافة"):
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)", (new_u, new_p, new_r))
                        conn.commit()
                        st.success("تمت إضافة المستخدم")
                        add_log(f"أضاف مستخدم جديد: {new_u}")
                    except: st.error("اسم المستخدم موجود مسبقاً")
                    conn.close()
            
            st.divider()
            st.subheader("المستخدمين الحاليين")
            st.dataframe(load_data("users")[['username', 'role']], use_container_width=True)
        else:
            st.warning("هذه الصلاحية متاحة للمدراء فقط")

    with tab2:
        st.subheader("تخصيص ألوان الواجهة")
        primary_color = st.color_picker("لون العنوان الرئيسي", "#1e293b")
        if st.button("حفظ التفضيلات"):
            st.success("تم حفظ إعدادات الواجهة (سيتم تطبيقها في التحديث القادم)")
            add_log("غير إعدادات الألوان")

    with tab3:
        st.subheader("النسخ الاحتياطي للبيانات")
        col_b1, col_b2 = st.columns(2)
        if col_b1.button("📤 إنشاء نسخة احتياطية الآن"):
            # محاكاة نسخ احتياطي بتحميل ملف CSV مجمع
            df_all = load_data("parents")
            st.download_button("تحميل البيانات (CSV)", df_all.to_csv().encode('utf-8-sig'), "backup.csv")
            add_log("أنشأ نسخة احتياطية للبيانات")
        
        col_b2.button("📥 استعادة نسخة (قريباً)")

    with tab4:
        st.subheader("📜 سجل نشاطات النظام")
        df_logs = load_data("logs").sort_values(by="id", ascending=False)
        st.dataframe(df_logs, use_container_width=True)

# (بقية التبويبات المعتادة تضاف هنا بنفس النمط السابق مع إضافة add_log عند كل عملية حفظ أو حذف)
elif menu == "👨‍👩‍👧‍👦 الشركاء":
    st.title("👨‍👩‍👧‍👦 إدارة الشركاء")
    with st.expander("➕ تسجيل شريك"):
        with st.form("p_f"):
            n = st.text_input("الاسم")
            t = st.selectbox("النوع", ["تعليمي", "مالي", "تطوعي"])
            if st.form_submit_button("حفظ"):
                conn = get_connection()
                conn.execute("INSERT INTO parents (name, participation_type) VALUES (?,?)", (n, t))
                conn.commit()
                conn.close()
                add_log(f"أضاف شريك جديد: {n}")
                st.rerun()
    st.dataframe(load_data("parents"), use_container_width=True)

elif menu == "🚀 المبادرات":
    st.title("🚀 المبادرات")
    # منطق المبادرات المطور سابقاً
    st.dataframe(load_data("initiatives"), use_container_width=True)
