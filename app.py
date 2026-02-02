import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection, init_db
from datetime import datetime, timedelta
import time
from streamlit_gsheets import GSheetsConnection

# إعدادات الصفحة
st.set_page_config(page_title="مساعد مشرف تنمية العلاقات المجتمعية", layout="wide", initial_sidebar_state="expanded")

# تهيئة قاعدة البيانات المحلية
init_db()

# محاولة الربط بجوجل شيت
try:
    conn_gs = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn_gs = None

# تنسيق CSS مخصص - ألوان هادئة ورسمية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Almarai:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', 'Almarai', sans-serif;
        direction: RTL;
        text-align: right;
    }
    
    .stApp {
        background-color: #f4f7f9;
    }

    /* القائمة الجانبية الرسمية */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50 !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #ecf0f1 !important;
    }

    /* تصميم البطاقات */
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-right: 5px solid #34495e;
    }
    
    div[data-testid="stMetricValue"] {
        color: #2c3e50 !important;
    }

    /* الأزرار الهادئة */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: #34495e;
        color: white;
        border: none;
        padding: 10px;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background: #2c3e50;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* شريط البحث */
    .search-box {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    h1 { color: #2c3e50; border-right: 8px solid #34495e; padding-right: 15px; }
    h2, h3 { color: #34495e; }
    </style>
    """, unsafe_allow_html=True)

# --- وظائف مساعدة ---
def load_data(table):
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    except Exception:
        init_db()
        try: df = pd.read_sql(f"SELECT * FROM {table}", conn)
        except: df = pd.DataFrame()
    conn.close()
    return df

# --- القائمة الجانبية ---
# الساعة والتاريخ
local_now = datetime.utcnow() + timedelta(hours=4)
st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 10px; border-bottom: 1px solid #3e4f5f;">
        <p style="color: #bdc3c7; font-size: 1.4rem; font-weight: 700; margin:0;">🕒 {local_now.strftime('%I:%M %p')}</p>
        <p style="color: #95a5a6; font-size: 0.8rem; margin:0;">📅 {local_now.strftime('%Y-%m-%d')}</p>
    </div>
""", unsafe_allow_html=True)

# البحث الذكي
st.sidebar.markdown('<div class="search-box">', unsafe_allow_html=True)
search_query = st.sidebar.text_input("🔍 بحث شامل...", placeholder="ابحث عن شريك، مبادرة...")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

menu = st.sidebar.radio(
    "المسار الإجرائي:",
    [
        "📊 لوحة التحكم", 
        "📅 خطة العمل", 
        "👨‍👩‍👧‍👦 الشركاء وأولياء الأمور", 
        "🚀 إدارة المبادرات", 
        "🎭 الفعاليات والأنشطة", 
        "📈 التقارير والإحصائيات", 
        "🤖 الذكاء الاصطناعي"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align:center; color:#95a5a6; font-size:0.7rem;'>تطوير: توفيق اليعقوبي</p>", unsafe_allow_html=True)

# --- معالجة البحث ---
if search_query:
    all_dfs = {"الشركاء": load_data("parents"), "المبادرات": load_data("initiatives"), "الخطة": load_data("action_plan")}
    with st.expander("🔎 نتائج البحث", expanded=True):
        for cat, df in all_dfs.items():
            if not df.empty:
                res = df[df.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)]
                if not res.empty:
                    st.write(f"**📍 في {cat}:**")
                    st.dataframe(res.drop(columns=['id'], errors='ignore'), use_container_width=True)

# --- التنقل بين التبويبات ---

if menu == "📊 لوحة التحكم":
    st.title("📊 لوحة القيادة المجتمعية")
    df_p = load_data("parents")
    df_i = load_data("initiatives")
    df_pl = load_data("action_plan")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("الشركاء", len(df_p))
    c2.metric("المبادرات", len(df_i))
    c3.metric("أهداف محققة", len(df_pl[df_pl['status'] == 'مكتمل']) if not df_pl.empty else 0)
    c4.metric("متوسط الأثر", f"{df_i['impact_score'].mean():.1f}" if not df_i.empty else "0.0")
    
    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📈 تفاعل الشركاء")
        if not df_p.empty:
            st.plotly_chart(px.pie(df_p, names='interaction_level', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
    with col_r:
        st.subheader("🚨 مهام عاجلة")
        urgent = df_pl[(df_pl['priority'] == 'مرتفع') & (df_pl['status'] != 'مكتمل')] if not df_pl.empty else pd.DataFrame()
        if not urgent.empty:
            for _, r in urgent.iterrows(): st.error(f"⚠️ {r['activity']}")
        else: st.success("لا توجد مهام متأخرة")

elif menu == "📅 خطة العمل":
    st.title("📅 خطة العمل السنوية")
    with st.expander("➕ إضافة بند جديد"):
        with st.form("pl_f"):
            obj = st.text_input("الهدف")
            act = st.text_input("النشاط")
            resp = st.text_input("المسؤول")
            prio = st.selectbox("الأولوية", ["مرتفع", "متوسط", "منخفض"])
            if st.form_submit_button("حفظ"):
                conn = get_connection()
                conn.execute("INSERT INTO action_plan (objective, activity, responsibility, priority, status) VALUES (?,?,?,?,'قيد التنفيذ')", (obj,act,resp,prio))
                conn.commit(); conn.close()
                st.rerun()
    
    df_pl = load_data("action_plan")
    if not df_pl.empty:
        st.data_editor(df_pl.drop(columns=['id']), use_container_width=True)

elif menu == "👨‍👩‍👧‍👦 الشركاء وأولياء الأمور":
    st.title("👨‍👩‍👧‍👦 إدارة الشركاء الاستراتيجيين")
    df_i = load_data("initiatives")
    
    with st.expander("➕ تسجيل شريك جديد"):
        with st.form("p_f"):
            name = st.text_input("الاسم")
            type_p = st.selectbox("مجال الشراكة", ["تعليمي", "مهني", "تطوعي", "مالي"])
            exp = st.text_input("الخبرة/المجال")
            if st.form_submit_button("إضافة شريك"):
                conn = get_connection()
                conn.execute("INSERT INTO parents (name, participation_type, expertise, interaction_level) VALUES (?,?,?,'متوسط')", (name, type_p, exp))
                conn.commit(); conn.close()
                st.rerun()

    df_p = load_data("parents")
    if not df_p.empty:
        for _, row in df_p.iterrows():
            with st.container():
                cl1, cl2 = st.columns([1, 2])
                cl1.markdown(f"### 👤 {row['name']}")
                cl1.caption(f"🛡️ {row['participation_type']} | {row['expertise']}")
                # الربط الذكي مع المبادرات
                if 'partner' in df_i.columns:
                    linked = df_i[df_i['partner'] == row['name']]
                    if not linked.empty:
                        cl2.write("**🚀 المبادرات المرتبطة:**")
                        for _, li in linked.iterrows(): cl2.info(f"🔹 {li['title']}")
                st.divider()

elif menu == "🚀 إدارة المبادرات":
    st.title("🚀 توثيق وإدارة المبادرات")
    df_p = load_data("parents")
    
    with st.expander("➕ توثيق مبادرة"):
        with st.form("i_f"):
            title = st.text_input("عنوان المبادرة")
            partner = st.selectbox("الشريك المرتبط", ["بدون شريك"] + df_p['name'].tolist()) if not df_p.empty else st.text_input("الشريك")
            status = st.selectbox("الحالة", ["قيد التنفيذ", "مكتملة", "مخطط لها"])
            impact = st.slider("الأثر", 1, 10, 5)
            if st.form_submit_button("توثيق"):
                conn = get_connection()
                try: conn.execute("INSERT INTO initiatives (title, partner, status, impact_score) VALUES (?,?,?,?)", (title, partner, status, impact))
                except:
                    conn.execute("ALTER TABLE initiatives ADD COLUMN partner TEXT")
                    conn.execute("INSERT INTO initiatives (title, partner, status, impact_score) VALUES (?,?,?,?)", (title, partner, status, impact))
                conn.commit(); conn.close()
                st.rerun()
    
    df_i = load_data("initiatives")
    if not df_i.empty:
        st.dataframe(df_i.drop(columns=['id']), use_container_width=True)

elif menu == "🎭 الفعاليات والأنشطة":
    st.title("🎭 إدارة الفعاليات")
    df_e = load_data("events")
    with st.form("e_f"):
        en = st.text_input("اسم الفعالية")
        ed = st.date_input("التاريخ")
        if st.form_submit_button("إضافة"):
            conn = get_connection()
            conn.execute("INSERT INTO events (name, date) VALUES (?,?)", (en, str(ed)))
            conn.commit(); conn.close()
            st.rerun()
    st.dataframe(df_e, use_container_width=True)

elif menu == "📈 التقارير والإحصائيات":
    st.title("📈 مركز التقارير")
    df_i = load_data("initiatives")
    if not df_i.empty:
        st.plotly_chart(px.bar(df_i, x='title', y='impact_score', color='status', title="أثر المبادرات المنفذة"), use_container_width=True)
    else: st.info("لا توجد بيانات كافية")

elif menu == "🤖 الذكاء الاصطناعي":
    st.title("🤖 مساعد الذكاء الاصطناعي")
    st.info("سيتم هنا تحليل البيانات واقتراح الخطابات الرسمية بناءً على سجل الشركاء والمبادرات.")
    # (المنطق الذي أضفناه سابقاً سيبقى هنا)
    st.subheader("✉️ مولد الخطابات الذكي")
    p_name = st.selectbox("اختر الشريك", load_data("parents")['name'].tolist()) if not load_data("parents").empty else "فلان"
    if st.button("توليد خطاب شكر"):
        st.code(f"نص الخطاب: نشكر الأستاذ {p_name} على جهوده المتميزة...")
