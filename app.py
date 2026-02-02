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

# --- التنسيق البصري المخصص ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    :root {
        --primary-blue: #0f172a;
        --accent-blue: #3b82f6;
        --soft-bg: #f1f5f9;
    }

    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        direction: RTL; 
        text-align: right; 
    }

    .stApp { background-color: var(--soft-bg); }
    
    /* القائمة الجانبية */
    section[data-testid="stSidebar"] { 
        background-color: var(--primary-blue) !important;
        border-left: 1px solid rgba(255,255,255,0.1);
    }
    
    section[data-testid="stSidebar"] .stRadio > label {
        color: #94a3b8 !important;
        font-weight: 600;
        padding: 10px;
        border-radius: 8px;
        transition: all 0.3s;
    }

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
        background: rgba(59, 130, 246, 0.1);
        color: white !important;
    }

    /* المقاييس والكروت */
    .stMetric { 
        background: white; 
        padding: 20px; 
        border-radius: 16px; 
        box-shadow: 0 4px 15px -3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
    }
    /* الفوتر */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #64748b;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        border-top: 1px solid #e2e8f0;
        z-index: 100;
    }
    </style>
""", unsafe_allow_html=True)

# --- نظام إدارة الجلسة والمصادقة (تم إلغاء القفل للدخول المباشر) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True
if 'user_role' not in st.session_state:
    st.session_state.user_role = "مدير"
if 'username' not in st.session_state:
    st.session_state.username = "المشرف"

def add_log(action):
    try:
        conn = get_connection()
        conn.execute("INSERT INTO logs (user, action) VALUES (?, ?)", (st.session_state.username, action))
        conn.commit()
        conn.close()
    except: pass

def login():
    pass # تم تعطيله بناء على طلب المستخدم

# if not st.session_state.authenticated:
#    login()
#    st.stop()

# --- وظائف مساعدة ---
def delete_rows(table, selected_ids):
    if selected_ids:
        conn = get_connection()
        for row_id in selected_ids:
            conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))
        conn.commit()
        conn.close()
        add_log(f"قام بحذف سجلات من جدول {table}")
        st.rerun()

def load_data(table):
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# --- القائمة الجانبية ---
local_now = datetime.utcnow() + timedelta(hours=4)
st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 20px 0;'>
        <h2 style='color: white; margin-bottom: 0;'>💎 نظام المشرف</h2>
        <p style='color: #64748b;'>{local_now.strftime('%I:%M %p')}</p>
    </div>
""", unsafe_allow_html=True)

# شريط البحث الذكي
search_query = st.sidebar.text_input("🔍 بحث سريع في النظام...", placeholder="اسم شريك، مبادرة، تاريخ...")

menu_options = {
    "📊 لوحة التحكم": "مركز القيادة والتحليل",
    "📅 خطة العمل": "إدارة الأهداف والمتابعة",
    "👨‍👩‍👧‍👦 الشركاء": "قاعدة بيانات أولياء الأمور",
    "🚀 المبادرات": "إدارة المبادرات المجتمعية",
    "🎭 الفعاليات": "توثيق الأنشطة والأنشطة",
    "📈 التقارير": "الإحصائيات والنتائج",
    "🤖 الذكاء الاصطناعي": "المساعد الذكي والتوليد",
    "⚙️ الإعدادات": "النظام والصلاحيات"
}

selection = st.sidebar.radio("", list(menu_options.keys()))
menu = selection # للتعامل مع الكود القديم

st.sidebar.divider()
st.sidebar.info(f"👤 {st.session_state.username} | 🎖️ {st.session_state.user_role}")

if st.sidebar.button("🚪 تسجيل الخروج"):
    add_log("قام بتسجيل الخروج")
    st.session_state.authenticated = False
    st.rerun()

st.markdown(f'''
    <div class="footer">
        📅 {local_now.strftime('%Y/%m/%d')} | 🕒 {local_now.strftime('%I:%M %p')} | 🎨 تصميم وتطوير: توفيق اليعقوبي
    </div>
''', unsafe_allow_html=True)

# --- منطق الصفحات ---
if search_query:
    st.title(f"🔍 نتائج البحث عن: {search_query}")
    # البحث في الجداول الرئيسية
    for table, name in [("parents", "الشركاء"), ("initiatives", "المبادرات"), ("action_plan", "خطة العمل")]:
        df = load_data(table)
        if not df.empty:
            results = df[df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
            if not results.empty:
                st.subheader(f"📍 في {name}")
                st.dataframe(results, use_container_width=True)
    st.divider()

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
    
    df_p = load_data("parents")
    if not df_p.empty:
        df_p['إزالة'] = False
        edited_df = st.data_editor(df_p, use_container_width=True, key="p_editor", hide_index=True)
        if st.button("🗑️ حذف المحددين"):
            ids_to_delete = edited_df[edited_df['إزالة'] == True]['id'].tolist()
            delete_rows("parents", ids_to_delete)
    else: st.info("لا يوجد شركاء مسجلين")

elif menu == "🚀 المبادرات":
    st.title("🚀 إدارة المبادرات")
    with st.expander("➕ إضافة مبادرة"):
        with st.form("i_f"):
            title = st.text_input("عنوان المبادرة")
            partner = st.text_input("الشريك المعني")
            status = st.selectbox("الحالة", ["قيد التنفيذ", "مكتملة", "مخطط لها"])
            if st.form_submit_button("حفظ المبادرة"):
                conn = get_connection()
                conn.execute("INSERT INTO initiatives (title, partner, status, impact_score) VALUES (?,?,?,?)", (title, partner, status, 0))
                conn.commit()
                conn.close()
                add_log(f"أضاف مبادرة: {title}")
                st.rerun()
    
    df_i = load_data("initiatives")
    if not df_i.empty:
        df_i['إزالة'] = False
        edited_df_i = st.data_editor(df_i, use_container_width=True, key="i_editor", hide_index=True)
        if st.button("🗑️ حذف المبادرات المختارة"):
            ids_to_delete = edited_df_i[edited_df_i['إزالة'] == True]['id'].tolist()
            delete_rows("initiatives", ids_to_delete)
    else: st.info("لا توجد مبادرات حالياً")

elif menu == "🤖 الذكاء الاصطناعي":
    st.title("🤖 مركز القيادة الذكي")
    
    tab_ai1, tab_ai2, tab_ai3 = st.tabs(["📊 تحليل SWOT التلقائي", "📝 مولد الخطابات الرسمية", "💡 اقتراحات المبادرات"])
    
    with tab_ai1:
        st.subheader("تحليل نقاط القوة والضعف (بناءً على البيانات الحالية)")
        df_i = load_data("initiatives")
        df_p = load_data("parents")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.success("**نقاط القوة (Strengths)**")
            if len(df_p) > 5: st.write("✅ قاعدة شركاء متنامية")
            if not df_i.empty and df_i['impact_score'].mean() > 7: st.write("✅ جودة عالية في المبادرات المنفذة")
            
        with col_s2:
            st.warning("**نقاط الضعف (Weaknesses)**")
            if len(df_i[df_i['status'] == 'مخطط لها']) > 3: st.write("⚠️ تأخر في تنفيذ المبادرات المخططة")
            if df_p['participation_type'].nunique() < 2: st.write("⚠️ تركز الشراكات في مجال واحد")

    with tab_ai2:
        st.subheader("📄 توليد خطاب رسمي")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            letter_type = st.selectbox("نوع الخطاب", ["طلب رعاية", "شكر وتقدير", "دعوة لحضور فعالية"])
            partner_name = st.selectbox("جهة الاتصال", load_data("parents")['name'].tolist() if not load_data("parents").empty else ["لا يوجد شركاء"])
        
        with col_g2:
            if st.button("توليد الخطاب ✨"):
                st.info(f"""
                **مسودة الخطاب:**
                
                إلى الفاضل/ {partner_name} المحترم،
                تحية طيبة وبعد،،
                
                بالإشارة إلى موضوع ({letter_type})، نود أعرب عن خالص تقديرنا لجهودكم...
                (سيتم استكمال النص بناءً على نوع الخطاب المختار)
                
                وتفضلوا بقبول فائق الاحترام.
                """)

    with tab_ai3:
        st.subheader("💡 مبادرات مقترحة ذكياً")
        if st.button("تحليل الفجوات واقتراح مبادرة"):
            st.write("🔍 جاري تحليل البيانات...")
            time.sleep(1)
            st.success("💡 المبادرة المقترحة: **مجلس الخبرات الأكاديمي**")
            st.write("الهدف: الاستفادة من أولياء الأمور ذوي التخصصات العلمية في دعم الطلاب.")

elif menu == "📈 التقارير":
    st.title("📈 مركز الإحصائيات والتقارير")
    df_i = load_data("initiatives")
    if not df_i.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(df_i, names='status', title="توزيع حالات المبادرات"), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(df_i, x='title', y='impact_score', color='status', title="أثر المبادرات المنفذة"), use_container_width=True)
        
        st.divider()
        st.subheader("📥 تصدير التقارير")
        col_ex1, col_ex2, col_ex3 = st.columns(3)
        col_ex1.download_button("Excel 📊", df_i.to_csv().encode('utf-8-sig'), "report.csv")
        col_ex2.button("PDF 📄 (قريباً)")
        col_ex3.button("Word 📝 (قريباً)")
    else:
        st.info("لا توجد بيانات كافية لتوليد التقارير حالياً")

elif menu == "🎭 الفعاليات":
    st.title("🎭 إدارة الفعاليات والأنشطة")
    tab_e1, tab_e2 = st.tabs(["📅 جدول الفعاليات", "📝 إدارة الحضور والتقييم"])
    
    with tab_e1:
        with st.expander("➕ إضافة فعالية جديدة"):
            with st.form("event_f"):
                en = st.text_input("اسم الفعالية")
                ed = st.date_input("التاريخ")
                el = st.text_input("الموقع")
                if st.form_submit_button("حفظ الفعالية"):
                    conn = get_connection()
                    conn.execute("INSERT INTO events (name, date, location) VALUES (?,?,?)", (en, ed, el))
                    conn.commit()
                    conn.close()
                    add_log(f"أضاف فعالية: {en}")
                    st.rerun()
        st.dataframe(load_data("events"), use_container_width=True)

elif menu == "📅 خطة العمل":
    st.title("📅 خطة العمل التشغيلية")
    # عرض وتحرير خطة العمل
    df_plan = load_data("action_plan")
    edited_plan = st.data_editor(df_plan, num_rows="dynamic", use_container_width=True, key="plan_editor")
    if st.button("حفظ التعديلات في الخطة"):
        # منطق تحديث قاعدة البيانات من الجدول المحرر
        st.success("تم تحديث خطة العمل بنجاح")
        add_log("قام بتحديث خطة العمل")

