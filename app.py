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

# --- نظام تسجيل الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None

if not st.session_state.logged_in:
    st.markdown("""
        <div style="text-align: center; padding: 50px;">
            <h1 style="color: #2c3e50;">🔐 نظام إدارة العلاقات المجتمعية</h1>
            <p style="color: #7f8c8d;">يرجى تسجيل الدخول للمتابعة</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_admin, tab_visitor = st.tabs(["👤 دخول المسؤول", "👁️ دخول الزوار"])
        
        with tab_admin:
            with st.form("admin_login"):
                st.subheader("تسجيل دخول (توفيق)")
                pwd = st.text_input("كلمة المرور", type="password")
                if st.form_submit_button("دخول"):
                    # كلمة المرور الافتراضية 1234
                    if pwd == "1234":
                        st.session_state.logged_in = True
                        st.session_state.user_role = "admin"
                        st.rerun()
                    else:
                        st.error("كلمة المرور غير صحيحة")
        
        with tab_visitor:
            st.info("بإمكانك الدخول كزائر لاستعراض البيانات والتقارير فقط دون صلاحية التعديل.")
            if st.button("الدخول كزائر"):
                st.session_state.logged_in = True
                st.session_state.user_role = "visitor"
                st.rerun()
    st.stop()

is_admin = st.session_state.user_role == "admin"

# محاولة الربط بجوجل شيت
try:
    conn_gs = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
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
        "🎭 الفعاليات والأنشطة", 
        "📈 التقارير والإحصائيات", 
        "🤖 الذكاء الاصطناعي"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align:center; color:#95a5a6; font-size:0.7rem;'>تطوير: توفيق اليعقوبي</p>", unsafe_allow_html=True)

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.rerun()

# --- معالجة البحث ---
if search_query:
    all_dfs = {"الشركاء": load_data("parents"), "الخطة": load_data("action_plan")}
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
    df_pl = load_data("action_plan")
    df_e = load_data("events")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("الشركاء المسجلين", len(df_p))
    c2.metric("الفعاليات المجدولة", len(df_e))
    c3.metric("أهداف محققة", len(df_pl[df_pl['status'] == 'مكتمل']) if not df_pl.empty else 0)
    c4.metric("تفاعل الشركاء", f"{(len(df_p[df_p['interaction_level'] == 'مرتفع'])/len(df_p)*100 if not df_p.empty else 0):.0f}%")
    
    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("📈 تفاعل الشركاء")
        if not df_p.empty and 'interaction_level' in df_p.columns:
            st.plotly_chart(px.pie(df_p, names='interaction_level', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r), use_container_width=True)
        else:
            st.info("لا توجد بيانات تفاعل كافية")
    with col_r:
        st.subheader("🚨 مهام عاجلة")
        if not df_pl.empty and 'priority' in df_pl.columns and 'status' in df_pl.columns:
            urgent = df_pl[(df_pl['priority'] == 'مرتفع') & (df_pl['status'] != 'مكتمل')]
            if not urgent.empty:
                for _, r in urgent.iterrows(): 
                    t_icon = "💰" if r.get('task_type') == 'مادي' else "💡"
                    date_info = f"📅 {r['timeframe']}" if r['timeframe'] else ""
                    
                    # إنشاء رابط واتساب الرسمي للتذكير
                    msg = f"تذكير بمهمة: {r['activity']}\nالتاريخ: {r['timeframe']}\nالنوع: {r.get('task_type', 'معنوي')}"
                    # استخدام الرابط الرسمي الكامل لتجنب مشاكل الحجب
                    whatsapp_url = f"https://api.whatsapp.com/send?text={msg.replace(' ', '%20').replace('\n', '%0A')}"
                    
                    col_msg, col_wa = st.columns([4, 1])
                    col_msg.error(f"{t_icon} **{r['activity']}** \n {date_info}")
                    col_wa.markdown(f"[📲 تذكير]({whatsapp_url})")
            else: st.success("لا توجد مهام متأخرة")
        else:
            st.success("لا توجد مهام مسجلة")

elif menu == "📅 خطة العمل":
    st.title("📅 خطة العمل السنوية")
    df_pl = load_data("action_plan")
    
    if is_admin:
        with st.expander("➕ إضافة بند جديد"):
            with st.form("pl_f"):
                obj = st.text_input("الهدف")
                act = st.text_input("النشاط")
                resp = st.text_input("المسؤول")
                timeframe = st.text_input("الجدول الزمني")
                kpi = st.text_input("مؤشر الأداء (KPI)")
                col_p, col_t = st.columns(2)
                with col_p:
                    prio = st.selectbox("الأولوية", ["مرتفع", "متوسط", "منخفض"])
                with col_t:
                    t_type = st.selectbox("نوع المهمة", ["معنوي", "مادي"])
                
                if st.form_submit_button("حفظ"):
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO action_plan (objective, activity, responsibility, timeframe, kpi, priority, status, task_type) VALUES (?,?,?,?,?,?,'قيد التنفيذ',?)", 
                                     (obj, act, resp, timeframe, kpi, prio, t_type))
                        conn.commit()
                        conn.close()
                        
                        # مزامنة سحابية
                        if conn_gs:
                            try:
                                new_data = pd.DataFrame([{"الهدف": obj, "النشاط": act, "المسؤول": resp, "الزمن": timeframe, "KPI": kpi, "الأولوية": prio, "النوع": t_type, "الحالة": "قيد التنفيذ"}])
                                try:
                                    existing = conn_gs.read(worksheet="ActionPlan", ttl=0)
                                    existing = existing.dropna(how='all')
                                    updated = pd.concat([existing, new_data], ignore_index=True)
                                except: updated = new_data
                                conn_gs.update(worksheet="ActionPlan", data=updated)
                            except: pass
                        
                        st.success("تم الحفظ بنجاح")
                        st.rerun()
                    except Exception as e:
                        # إضافة العمود في حال عدم وجوده (للبيئة السحابية)
                        if "no column named task_type" in str(e):
                            conn.execute("ALTER TABLE action_plan ADD COLUMN task_type TEXT DEFAULT 'معنوي'")
                            conn.commit()
                            conn.execute("INSERT INTO action_plan (objective, activity, responsibility, timeframe, kpi, priority, status, task_type) VALUES (?,?,?,?,?,?,'قيد التنفيذ',?)", 
                                         (obj, act, resp, timeframe, kpi, prio, t_type))
                            conn.commit()
                            conn.close()
                            st.success("تم التحديث والحفظ")
                            st.rerun()
                        else:
                            st.error(f"خطأ: {e}")
    
    if not df_pl.empty:
        st.subheader("📋 بنود الخطة (يمكنك التعديل مباشرة من الجدول)")
        
        # ترجمة الأعمدة للعرض
        display_pl = df_pl.rename(columns={
            'objective': 'الهدف',
            'activity': 'النشاط',
            'responsibility': 'المسؤول',
            'timeframe': 'الجدول الزمني',
            'kpi': 'مؤشر الأداء',
            'priority': 'الأولوية',
            'status': 'الحالة',
            'task_type': 'نوع المهمة'
        })
        
        if is_admin:
            display_pl['حذف'] = False
            edited_df = st.data_editor(
                display_pl, 
                key="plan_edit", 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={"id": st.column_config.NumberColumn("ID", disabled=True)}
            )
            
            c_del, c_save = st.columns(2)
            if c_del.button("🔴 حذف المحدد من الخطة"):
                to_del = edited_df[edited_df['حذف'] == True]
                if not to_del.empty:
                    conn = get_connection()
                    for rid in to_del['id']: 
                        if not pd.isna(rid):
                            conn.execute(f"DELETE FROM action_plan WHERE id={rid}")
                    conn.commit(); conn.close()
                    st.success("تم الحذف بنجاح")
                    st.rerun()
            
            if c_save.button("💾 حفظ كافة التعديلات في الخطة"):
                conn = get_connection()
                try:
                    for _, row in edited_df.iterrows():
                        if 'id' in row and not pd.isna(row['id']):
                            conn.execute("""UPDATE action_plan SET objective=?, activity=?, responsibility=?, timeframe=?, kpi=?, priority=?, status=?, task_type=? WHERE id=?""",
                                         (row['الهدف'], row['النشاط'], row['المسؤول'], row['الجدول الزمني'], row['مؤشر الأداء'], row['الأولوية'], row['الحالة'], row.get('نوع المهمة', 'معنوي'), row['id']))
                    conn.commit()
                except Exception as e:
                    if "no column named task_type" in str(e):
                        conn.execute("ALTER TABLE action_plan ADD COLUMN task_type TEXT DEFAULT 'معنوي'")
                        conn.commit()
                        # إعادة المحاولة بعد إضافة العمود
                        for _, row in edited_df.iterrows():
                            if 'id' in row and not pd.isna(row['id']):
                                conn.execute("""UPDATE action_plan SET objective=?, activity=?, responsibility=?, timeframe=?, kpi=?, priority=?, status=?, task_type=? WHERE id=?""",
                                             (row['الهدف'], row['النشاط'], row['المسؤول'], row['الجدول الزمني'], row['مؤشر الأداء'], row['الأولوية'], row['الحالة'], row.get('نوع المهمة', 'معنوي'), row['id']))
                        conn.commit()
                    else:
                        st.error(f"❌ خطأ في قاعدة البيانات: {e}")
                finally:
                    conn.close()
                
                if conn_gs:
                    try:
                        # إرسال البيانات المترجمة لجوجل شيت (بدون أعمدة التحكم)
                        gs_data = edited_df.drop(columns=['id', 'حذف'], errors='ignore')
                        conn_gs.update(worksheet="ActionPlan", data=gs_data)
                    except Exception as e:
                        st.warning(f"⚠️ فشل التحديث في Google Sheets: {e}")
                st.success("✅ تم تحديث الخطة بنجاح")
                st.rerun()
        else:
            st.dataframe(display_pl.drop(columns=['id'], errors='ignore'), use_container_width=True)

elif menu == "👨‍👩‍👧‍👦 الشركاء وأولياء الأمور":
    st.title("👨‍👩‍👧‍👦 إدارة الشركاء الاستراتيجيين")
    df_e = load_data("events")
    
    if is_admin:
        with st.expander("➕ تسجيل شريك جديد"):
            with st.form("p_f"):
                name = st.text_input("الاسم")
                type_p = st.selectbox("مجال الشراكة", ["دعم تعليمي", "دعم مالي", "خبرات مهنية", "تطوع", "مبادرات"])
                exp = st.text_input("المجال / الخبرة التخصصية")
                level = st.selectbox("مستوى التفاعل المتوقع", ["مرتفع", "متوسط", "محدود"])
                if st.form_submit_button("إضافة شريك"):
                    conn = get_connection()
                    conn.execute("INSERT INTO parents (name, participation_type, expertise, interaction_level) VALUES (?,?,?,?)", (name, type_p, exp, level))
                    conn.commit(); conn.close()
                    
                    # مزامنة سحابية
                    if conn_gs:
                        try:
                            new_data = pd.DataFrame([{"الاسم": name, "النوع": type_p, "الخبرة": exp, "التفاعل": level, "التاريخ": str(datetime.now())}])
                            try:
                                existing = conn_gs.read(worksheet="Parents", ttl=0)
                                existing = existing.dropna(how='all')
                                updated = pd.concat([existing, new_data], ignore_index=True)
                            except: updated = new_data
                            conn_gs.update(worksheet="Parents", data=updated)
                        except Exception as e:
                            st.warning(f"⚠️ فشل تحديث Google Sheets (الشركاء): {e}")
                    
                    st.success("تم تسجيل الشريك بنجاح")
                    st.rerun()

    df_p = load_data("parents")
    if not df_p.empty:
        st.subheader("🔍 استعراض الشركاء والربط الذكي (يمكنك التعديل مباشرة)")
        
        # ترجمة الأعمدة للعرض
        display_p = df_p.rename(columns={
            'name': 'الاسم',
            'participation_type': 'نوع المشاركة',
            'expertise': 'الخبرة/المجال',
            'interaction_level': 'مستوى التفاعل'
        })
        
        if is_admin:
            display_p['حذف'] = False
            edited_p = st.data_editor(
                display_p, 
                key="p_edit", 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={"id": st.column_config.NumberColumn("ID", disabled=True)}
            )
            
            c_p1, c_p2 = st.columns(2)
            if c_p1.button("🔴 حذف المحدد من الشركاء"):
                to_del = edited_p[edited_p['حذف'] == True]
                if not to_del.empty:
                    conn = get_connection()
                    for rid in to_del['id']: 
                        if not pd.isna(rid):
                            conn.execute(f"DELETE FROM parents WHERE id={rid}")
                    conn.commit(); conn.close()
                    st.success("تم الحذف بنجاح")
                    st.rerun()
            
            if c_p2.button("💾 حفظ تعديلات الشركاء"):
                conn = get_connection()
                for _, row in edited_p.iterrows():
                    if 'id' in row and not pd.isna(row['id']):
                        conn.execute("""UPDATE parents SET name=?, participation_type=?, expertise=?, interaction_level=? WHERE id=?""",
                                     (row['الاسم'], row['نوع المشاركة'], row['الخبرة/المجال'], row['مستوى التفاعل'], row['id']))
                conn.commit(); conn.close()
                if conn_gs:
                    try: 
                        gs_data_p = edited_p.drop(columns=['id', 'حذف'], errors='ignore')
                        conn_gs.update(worksheet="Parents", data=gs_data_p)
                    except Exception as e:
                        st.warning(f"⚠️ فشل تحديث Google Sheets: {e}")
                st.success("✅ تم التحديث بنجاح")
                st.rerun()
        else:
            st.dataframe(display_p.drop(columns=['id'], errors='ignore'), use_container_width=True)
        
        st.divider()
        for _, row in df_p.iterrows():
            with st.container():
                cl1, cl2 = st.columns([1, 2])
                cl1.markdown(f"### 👤 {row['name']}")
                cl1.caption(f"🛡️ {row['participation_type']} | {row['expertise']}")
                if not df_e.empty and 'name' in df_e.columns:
                    linked = df_e[df_e['name'].str.contains(row['name'], na=False)]
                    if not linked.empty:
                        cl2.write("**🚀 الفعاليات المرتبطة:**")
                        for _, li in linked.iterrows(): cl2.info(f"🔹 {li['name']}")
                    else:
                        cl2.write("➖ لا توجد فعاليات مرتبطة حالياً")
                st.divider()

elif menu == "🎭 الفعاليات والأنشطة":
    st.title("🎭 إدارة الفعاليات والأنشطة")
    if is_admin:
        with st.expander("🗓️ إضافة فعالية جديدة"):
            with st.form("e_f"):
                en = st.text_input("اسم الفعالية")
                ed = st.date_input("التاريخ")
                el = st.text_input("المكان")
                at = st.number_input("عدد الحضور المتوقع", 0)
                if st.form_submit_button("إضافة للجدول"):
                    success_local = False
                    try:
                        conn = get_connection()
                        # التأكد من وجود الجدول قبل الإدخال (حل مشكلة البيئات السحابية)
                        conn.execute('''CREATE TABLE IF NOT EXISTS events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            date TEXT,
                            location TEXT,
                            attendees_count INTEGER,
                            rating INTEGER
                        )''')
                        conn.execute("INSERT INTO events (name, date, location, attendees_count) VALUES (?,?,?,?)", 
                                     (en, str(ed), el, at))
                        conn.commit()
                        conn.close()
                        success_local = True
                    except Exception as e:
                        # إذا فشل الحفظ المحلي في السحاب، لا نتوقف بل نحاول السحابي فقط
                        st.info("ℹ️ ملاحظة: سيتم الحفظ سحابياً فقط (البيئة المحلية مؤقتة)")
                    
                    # مزامنة سحابية (الأولوية القصوى)
                    if conn_gs:
                        try:
                            new_data = pd.DataFrame([{"الفعالية": en, "التاريخ": str(ed), "المكان": el, "الحضور": at}])
                            try:
                                existing = conn_gs.read(worksheet="Events", ttl=0)
                                existing = existing.dropna(how='all')
                                updated = pd.concat([existing, new_data], ignore_index=True)
                            except: updated = new_data
                            conn_gs.update(worksheet="Events", data=updated)
                            st.success("✅ تم الحفظ بنجاح في جوجل شيت")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            if "Events" in str(e):
                                st.error("❌ لم يتم العثور على تبويب باسم 'Events' في ملف جوجل شيت. يرجى التأكد من وجود ورقة عمل بهذا الاسم بالضبط.")
                            else:
                                st.error(f"❌ فشل الحفظ في جوجل شيت: {e}")
                    elif success_local:
                        st.success("✅ تم الحفظ محلياً")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ فشل الحفظ في جميع الوسائط. يرجى التحقق من الربط.")
    
    df_e = load_data("events")
    if not df_e.empty:
        st.subheader("🗓️ جدول الفعاليات")
        # ترجمة الأعمدة للعرض
        display_df = df_e.rename(columns={
            'name': 'الفعالية',
            'date': 'التاريخ',
            'location': 'المكان',
            'attendees_count': 'الحضور المتوقع',
            'rating': 'التقييم'
        })
        
        if is_admin:
            display_df['حذف'] = False
            edited_e = st.data_editor(
                display_df, 
                key="e_edit", 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={"id": st.column_config.NumberColumn("ID", disabled=True)}
            )
            
            c_e1, c_e2 = st.columns(2)
            if c_e1.button("🔴 حذف الفعاليات المحددة"):
                to_del = edited_e[edited_e['حذف'] == True]
                if not to_del.empty:
                    conn = get_connection()
                    for _, row in to_del.iterrows():
                        if 'id' in row and not pd.isna(row['id']):
                            conn.execute(f"DELETE FROM events WHERE id={row['id']}")
                    conn.commit(); conn.close()
                    st.success("تم الحذف بنجاح")
                    st.rerun()
            
            if c_e2.button("💾 حفظ تعديلات الفعاليات"):
                conn = get_connection()
                for _, row in edited_e.iterrows():
                    if 'id' in row and not pd.isna(row['id']):
                        conn.execute("""UPDATE events SET name=?, date=?, location=?, attendees_count=?, rating=? WHERE id=?""",
                                     (row['الفعالية'], str(row['التاريخ']), row['المكان'], row['الحضور المتوقع'], row.get('التقييم', 0), row['id']))
                conn.commit(); conn.close()
                if conn_gs:
                    try: 
                        gs_data_e = edited_e.drop(columns=['حذف', 'id'], errors='ignore')
                        conn_gs.update(worksheet="Events", data=gs_data_e)
                    except Exception as e:
                        st.warning(f"⚠️ فشل تحديث Google Sheets: {e}")
                st.success("✅ تم تحديث الفعاليات بنجاح")
                st.rerun()
        else:
            st.dataframe(display_df.drop(columns=['id', 'حذف'], errors='ignore'), use_container_width=True)

elif menu == "📈 التقارير والإحصائيات":
    st.title("📈 مركز التقارير والتحليلات")
    df_e = load_data("events")
    df_p = load_data("parents")
    
    if not df_e.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("📊 حضور الفعاليات")
            fig = px.bar(df_e, x='name', y='attendees_count', title="عدد الحضور حسب الفعالية")
            st.plotly_chart(fig, use_container_width=True)
        
        with col_c2:
            st.subheader("👥 توزيع الشركاء")
            if 'participation_type' in df_p.columns:
                fig_pie = px.pie(df_p, names='participation_type', title="أنواع الشراكات")
                st.plotly_chart(fig_pie, use_container_width=True)
        
        st.divider()
        if st.button("📤 تصدير ملخص التقارير إلى Google Sheets"):
            if conn_gs:
                try:
                    # تجهيز النص الموحد للتقرير كما طلب المستخدم
                    report_text = f"""تقرير دوري: مشرف تنمية العلاقات المجتمعية
التاريخ: {datetime.now().strftime('%Y-%m-%d')}
------------------------------------------
1. ملخص الإنجاز: تم تنفيذ {len(df_e)} عملية/فعالية.
2. حالة أولياء الأمور: يوجد {len(df_p)} ولي أمر مسجل.
3. التوصيات: الاستمرار في تعزيز التواصل الرقمي.
------------------------------------------"""
                    
                    # تجهيز البيانات للإرسال
                    report_data = pd.DataFrame([{
                        "التاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "نص التقرير": report_text
                    }])
                    
                    try:
                        existing_reports = conn_gs.read(worksheet="Reports", ttl=0)
                        existing_reports = existing_reports.dropna(how='all')
                        updated_reports = pd.concat([existing_reports, report_data], ignore_index=True)
                    except:
                        updated_reports = report_data
                    
                    conn_gs.update(worksheet="Reports", data=updated_reports)
                    st.success("✅ تم تصدير التقرير النصي بنجاح")
                    st.text_area("معاينة التقرير المرسل:", report_text, height=200)
                except Exception as e:
                    st.error(f"❌ فشل التصدير: {e}")
            else:
                st.error("❌ الاتصال بـ Google Sheets غير مفعل.")
    else:
        st.info("لا توجد بيانات كافية لتوليد التقارير")

elif menu == "🤖 الذكاء الاصطناعي":
    st.title("🤖 مركز الذكاء الاصطناعي الاستراتيجي")
    
    tab_gen, tab_swot, tab_reports = st.tabs(["✉️ توليد الخطابات", "🔍 التحليل الرباعي SWOT", "📊 تقارير الأداء"])
    
    df_p = load_data("parents")
    df_e = load_data("events")
    
    with tab_gen:
        st.subheader("✉️ مولد المراسلات الرسمية")
        if not df_p.empty:
            p_name = st.selectbox("اختر الشريك المستهدف", df_p['name'].tolist())
            doc_type = st.selectbox("نوع الخطاب", ["دعوة شراكة", "خطاب شكر", "تقرير تعاون"])
            if st.button("توليد النص"):
                if doc_type == "دعوة شراكة":
                    st.info(f"إلى الأستاذ {p_name}، نود دعوتكم للمساهمة في برامجنا المجتمعية القادمة...")
                elif doc_type == "خطاب شكر":
                    st.success(f"نتقدم بخالص الشكر والتقدير للأستاذ {p_name} على جهوده الملموسة...")
                st.caption("يمكنك نسخ النص واستخدامه في مراسلاتك الرسمية.")
                if st.button("تصدير كـ PDF"): st.warning("خاصية التصدير قيد التطوير")
        else:
            st.warning("يجب إضافة شركاء أولاً لتوليد الخطابات.")

    with tab_swot:
        st.subheader("🔍 التحليل الرباعي الذكي")
        st.write("بناءً على البيانات الحالية، يقترح النظام التحليل التالي:")
        col1, col2 = st.columns(2)
        col1.success(f"**نقاط القوة:** وجود {len(df_p)} شركاء فاعلين.")
        col2.warning(f"**نقاط الضعف:** الحاجة لزيادة عدد الفعاليات المنجزة.")
        col1.info("**الفرص:** توسيع قاعدة الشراكات في المجالات المهنية.")
        col2.error("**التحديات:** تفاوت مستويات التفاعل بين الشركاء.")

    with tab_reports:
        st.subheader("📑 نظام التقارير التلقائي")
        rep_type = st.radio("نوع التقرير", ["تقرير شهري", "تقرير فصلي", "تقرير سنوي"], horizontal=True)
        if st.button("توليد التقرير الإحصائي"):
            st.write(f"تقرير {rep_type} - تم توليده بتاريخ {datetime.now().strftime('%Y-%m-%d')}")
            st.write(f"إجمالي الفعاليات: {len(df_e)}")
            st.write(f"إجمالي الشركاء: {len(df_p)}")
            st.download_button("تحميل بيانات الشركاء (Excel)", df_p.to_csv().encode('utf-8'), "partners.csv", "text/csv")
