import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_connection, init_db
from datetime import datetime, timedelta
import time

# إعدادات الصفحة
st.set_page_config(page_title="مساعد مشرف تنمية العلاقات المجتمعية", layout="wide", initial_sidebar_state="auto")

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

# تنسيق CSS مخصص - ألوان هادئة ورسمية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Almarai:wght@400;700&display=swap');
    
    /* تنسيق المحتوى ليدعم العربية دون كسر الهيكل */
    [data-testid="stMain"], [data-testid="stSidebarContent"], [data-testid="stHeader"] {
        direction: RTL;
        text-align: right;
    }

    .stApp {
        background-color: #f4f7f9;
    }

    /* تحسين استجابة الهواتف */
    @media (max-width: 768px) {
        .stMain {
            padding: 10px !important;
        }
        div[data-testid="metric-container"] {
            padding: 10px !important;
            margin-bottom: 10px;
        }
        h1 { font-size: 1.5rem !important; }
    }

    /* القائمة الجانبية الرسمية */
    section[data-testid="stSidebar"] {
        background-color: #2c3e50 !important;
        min-width: 300px !important;
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
    section[data-testid="stSidebar"] .stTextInput input {
        color: #00008B !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
        border: 2px solid #34495e !important;
        border-radius: 10px !important;
    }
    
    h1 { color: #2c3e50; border-right: 8px solid #34495e; padding-right: 15px; }
    h2, h3 { color: #34495e; }
    </style>
    """, unsafe_allow_html=True)

# --- وظائف مساعدة ---
def load_data(table):
    init_db() # التأكد من وجود الجداول أولاً
    conn = get_connection()
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

# --- القائمة الجانبية ---
with st.sidebar:
    st.components.v1.html(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@700&display=swap');
            body {{
                background-color: transparent;
                margin: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                font-family: 'Cairo', sans-serif;
                overflow: hidden;
            }}
            #time {{ color: #bdc3c7; font-size: 1.4rem; font-weight: 700; margin:0; }}
            #date {{ color: #95a5a6; font-size: 0.8rem; margin:0; }}
        </style>
        <div id="time">🕒 --:--:--</div>
        <div id="date">📅 ----</div>
        <script>
            function update() {{
                const now = new Date();
                const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
                const gmt4 = new Date(utc + (3600000 * 4));
                const h = gmt4.getHours();
                const m = gmt4.getMinutes().toString().padStart(2, '0');
                const s = gmt4.getSeconds().toString().padStart(2, '0');
                const ampm = h >= 12 ? 'PM' : 'AM';
                const hours = (h % 12 || 12).toString().padStart(2, '0');
                document.getElementById('time').innerText = '🕒 ' + hours + ':' + m + ':' + s + ' ' + ampm;
                document.getElementById('date').innerText = '📅 ' + gmt4.toISOString().split('T')[0];
            }}
            setInterval(update, 1000);
            update();
        </script>
    """, height=90)
    st.sidebar.markdown('<div style="border-bottom: 1px solid #3e4f5f; margin-bottom: 10px;"></div>', unsafe_allow_html=True)

# البحث الذكي
search_query = st.sidebar.text_input("🔍 بحث شامل...", placeholder="ابحث عن شريك، مبادرة...")

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
                    st.error(f"{t_icon} **{r['activity']}** \n {date_info}")
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
                timeframe = st.date_input("الجدول الزمني")
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
                                     (obj, act, resp, str(timeframe), kpi, prio, t_type))
                        conn.commit()
                        conn.close()
                        st.success("تم الحفظ بنجاح")
                        st.rerun()
                    except Exception as e:
                        if "no column named task_type" in str(e):
                            conn.execute("ALTER TABLE action_plan ADD COLUMN task_type TEXT DEFAULT 'معنوي'")
                            conn.commit()
                            conn.execute("INSERT INTO action_plan (objective, activity, responsibility, timeframe, kpi, priority, status, task_type) VALUES (?,?,?,?,?,?,'قيد التنفيذ',?)", 
                                         (obj, act, resp, str(timeframe), kpi, prio, t_type))
                            conn.commit()
                            conn.close()
                            st.success("تم التحديث والحفظ")
                            st.rerun()
                        else:
                            st.error(f"خطأ: {e}")
    
    if not df_pl.empty:
        st.subheader("📋 بنود الخطة (يمكنك التعديل مباشرة من الجدول)")
        try:
            df_pl['timeframe'] = pd.to_datetime(df_pl['timeframe'], errors='coerce')
        except:
            pass
            
        display_pl = df_pl.rename(columns={
            'objective': 'الهدف', 'activity': 'النشاط', 'responsibility': 'المسؤول',
            'timeframe': 'الجدول الزمني', 'kpi': 'مؤشر الأداء', 'priority': 'الأولوية',
            'status': 'الحالة', 'task_type': 'نوع المهمة'
        })
        
        if is_admin:
            display_pl['حذف'] = False
            edited_df = st.data_editor(
                display_pl, 
                key="plan_edit", 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "الجدول الزمني": st.column_config.DateColumn("الجدول الزمني")
                }
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
                    st.success("تم الحفظ بنجاح")
                    st.rerun()
            
            if c_save.button("💾 حفظ كافة التعديلات في الخطة"):
                conn = get_connection()
                try:
                    for _, row in edited_df.iterrows():
                        if 'id' in row and not pd.isna(row['id']):
                            conn.execute("""UPDATE action_plan SET objective=?, activity=?, responsibility=?, timeframe=?, kpi=?, priority=?, status=?, task_type=? WHERE id=?""",
                                         (row['الهدف'], row['النشاط'], row['المسؤول'], str(row['الجدول الزمني']), row['مؤشر الأداء'], row['الأولوية'], row['الحالة'], row.get('نوع المهمة', 'معنوي'), row['id']))
                    conn.commit()
                except Exception as e:
                    if "no column named task_type" in str(e):
                        conn.execute("ALTER TABLE action_plan ADD COLUMN task_type TEXT DEFAULT 'معنوي'")
                        conn.commit()
                        for _, row in edited_df.iterrows():
                            if 'id' in row and not pd.isna(row['id']):
                                conn.execute("""UPDATE action_plan SET objective=?, activity=?, responsibility=?, timeframe=?, kpi=?, priority=?, status=?, task_type=? WHERE id=?""",
                                             (row['الهدف'], row['النشاط'], row['المسؤول'], str(row['الجدول الزمني']), row['مؤشر الأداء'], row['الأولوية'], row['الحالة'], row.get('نوع المهمة', 'معنوي'), row['id']))
                        conn.commit()
                    else:
                        st.error(f"❌ خطأ في قاعدة البيانات: {e}")
                finally:
                    conn.close()
                st.success("✅ تم تحديث الخطة بنجاح")
                st.rerun()
        else:
            st.dataframe(display_pl.drop(columns=['id'], errors='ignore'), use_container_width=True)

elif menu == "👨‍👩‍👧‍👦 الشركاء وأولياء الأمور":
    st.title("👨‍👩‍👧‍👦 إدارة الشركاء الاستراتيجيين")
    
    if is_admin:
        with st.expander("➕ تسجيل شريك جديد"):
            with st.form("p_f"):
                name = st.text_input("الاسم")
                type_p = st.selectbox("مجال الشراكة", ["دعم تعليمي", "دعم مالي", "خبرات مهنية", "تطوع", "مبادرات"])
                exp = st.text_input("المجال / الخبرة التخصصية")
                level = st.selectbox("مستوى التفاعل المتوقع", ["مرتفع", "متوسط", "محدود"])
                phone = st.text_input("رقم الهاتف")
                if st.form_submit_button("إضافة شريك"):
                    conn = get_connection()
                    try:
                        conn.execute("INSERT INTO parents (name, participation_type, expertise, interaction_level, phone) VALUES (?,?,?,?,?)", (name, type_p, exp, level, phone))
                        conn.commit()
                    except Exception as e:
                        if "no column named phone" in str(e):
                            conn.execute("ALTER TABLE parents ADD COLUMN phone TEXT")
                            conn.commit()
                            conn.execute("INSERT INTO parents (name, participation_type, expertise, interaction_level, phone) VALUES (?,?,?,?,?)", (name, type_p, exp, level, phone))
                            conn.commit()
                        else:
                            st.error(f"خطأ: {e}")
                    finally:
                        conn.close()
                    st.success("تم تسجيل الشريك بنجاح")
                    st.rerun()

    df_p = load_data("parents")
    if not df_p.empty:
        st.subheader("🔍 استعراض الشركاء والربط الذكي")
        
        # ترجمة الأعمدة للعرض
        display_p = df_p.rename(columns={
            'name': 'الاسم', 'participation_type': 'نوع المشاركة',
            'expertise': 'الخبرة/المجال', 'interaction_level': 'مستوى التفاعل',
            'phone': 'رقم الهاتف'
        })
        
        # إعادة وظيفة رابط واتساب الذكي
        def make_ai_whatsapp_link(row):
            phone = row.get('رقم الهاتف')
            name = row.get('الاسم')
            p_type = row.get('نوع المشاركة')
            if phone and name:
                message = f"""الأخ الفاضل الأستاذ {name} المحترم،،\n\nالسلام عليكم ورحمة الله وبركاته..\nيسرنا في قسم تنمية العلاقات المجتمعية أن نتقدم لشخصكم الكريم بخالص الشكر على مساهماتكم في مجال ({p_type}). نتطلع دوماً لاستمرار هذا التعاون المثمر.\n\nتفضلوا بقبول فائق التقدير،،\nمشرف تنمية العلاقات المجتمعية"""
                clean_phone = ''.join(filter(str.isdigit, str(phone)))
                encoded_msg = message.replace(' ', '%20').replace('\n', '%0A')
                return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_msg}"
            return ""

        if is_admin:
            display_p['واتساب الذكي'] = display_p.apply(make_ai_whatsapp_link, axis=1)
            display_p['حذف'] = False
            edited_p = st.data_editor(
                display_p, 
                key="p_edit", 
                use_container_width=True, 
                num_rows="dynamic",
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "واتساب الذكي": st.column_config.LinkColumn("🤖 مراسلة ذكية", display_text="إرسال شكر ذكي")
                }
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
                        conn.execute("""UPDATE parents SET name=?, participation_type=?, expertise=?, interaction_level=?, phone=? WHERE id=?""",
                                     (row['الاسم'], row['نوع المشاركة'], row['الخبرة/المجال'], row['مستوى التفاعل'], row.get('رقم الهاتف', ''), row['id']))
                conn.commit(); conn.close()
                st.success("✅ تم التحديث بنجاح")
                st.rerun()
        else:
            st.dataframe(display_p.drop(columns=['id', 'رقم الهاتف'], errors='ignore'), use_container_width=True)
        
        # --- إعادة عرض البطاقات التعريفية للشركاء ---
        st.divider()
        st.subheader("📋 بطاقات التواصل السريع")
        for _, row in df_p.iterrows():
            with st.container():
                col_c1, col_c2 = st.columns([1, 2])
                with col_c1:
                    st.markdown(f"### 👤 {row['name']}")
                    st.caption(f"🛡️ {row['participation_type']} | {row['expertise']}")
                
                with col_c2:
                    if is_admin and row.get('phone'):
                        clean_p = ''.join(filter(str.isdigit, str(row['phone'])))
                        msg = f"السلام عليكم الأستاذ {row['name']}، نثمن دوركم في {row['participation_type']}."
                        wa_url = f"https://api.whatsapp.com/send?phone={clean_p}&text={msg.replace(' ', '%20')}"
                        st.markdown(f"### [💬 مراسلة فورية]({wa_url})")
                    else:
                        st.write("➖ لا توجد بيانات اتصال")
                st.markdown("---")

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
                    try:
                        conn = get_connection()
                        conn.execute("INSERT INTO events (name, date, location, attendees_count) VALUES (?,?,?,?)", 
                                     (en, str(ed), el, at))
                        conn.commit(); conn.close()
                        st.success("تمت الإضافة")
                        st.rerun()
                    except Exception as e:
                        st.error(f"خطأ: {e}")

    df_e = load_data("events")
    if not df_e.empty:
        display_e = df_e.rename(columns={
            'name': 'الفعالية', 'date': 'التاريخ', 'location': 'المكان', 
            'attendees_count': 'الحضور', 'rating': 'التقييم'
        })
        if is_admin:
            display_e['حذف'] = False
            edited_e = st.data_editor(display_e, key="e_edit", use_container_width=True, num_rows="dynamic")
            
            c_e1, c_e2 = st.columns(2)
            if c_e1.button("🔴 حذف الفعالية"):
                to_del = edited_e[edited_e['حذف'] == True]
                if not to_del.empty:
                    conn = get_connection()
                    for _, row in to_del.iterrows():
                        conn.execute(f"DELETE FROM events WHERE id={row['id']}")
                    conn.commit(); conn.close()
                    st.success("تم الحذف")
                    st.rerun()
            
            if c_e2.button("💾 حفظ تعديلات الفعاليات"):
                conn = get_connection()
                for _, row in edited_e.iterrows():
                    if 'id' in row and not pd.isna(row['id']):
                        conn.execute("""UPDATE events SET name=?, date=?, location=?, attendees_count=?, rating=? WHERE id=?""",
                                     (row['الفعالية'], str(row['التاريخ']), row['المكان'], row['الحضور'], row.get('التقييم', 0), row['id']))
                conn.commit(); conn.close()
                st.success("✅ تم التحديث")
                st.rerun()
        else:
            st.dataframe(display_e.drop(columns=['id'], errors='ignore'), use_container_width=True)

elif menu == "🤖 الذكاء الاصطناعي":
    st.title("🤖 مساعدك الذكي لتطوير العلاقات")
    
    df_p = load_data("parents")
    
    tab_gen, tab_wa = st.tabs(["💡 اقتراح مبادرات", "💬 صياغة رسائل واتساب"])
    
    with tab_gen:
        task = st.selectbox("اختر نوع التحليل الذكي:", ["اقتراح مبادرة مجتمعية جديدة", "تحليل معوقات الخطة السنوية"])
        if st.button("توليد الفكرة الذكية"):
            with st.spinner("جاري التفكير..."):
                time.sleep(1.5)
                if "مبادرة" in task:
                    st.success("**مبادرة جسور المعرفة:** ربط خبرات أولياء الأمور المهنية باحتياجات الطلاب عبر ورش عمل شهرية.")
                else:
                    st.warning("يُنصح بزيادة وتيرة التواصل مع الشركاء ذوي التفاعل 'المحدود' لتحويلهم لشركاء استراتيجيين.")

    with tab_wa:
        if df_p.empty:
            st.warning("يرجى إضافة شركاء أولاً")
        else:
            selected_parent = st.selectbox("اختر الشريك للمراسلة:", df_p['name'].tolist())
            parent_info = df_p[df_p['name'] == selected_parent].iloc[0]
            
            msg_style = st.radio("أسلوب الرسالة:", ["رسمي جداً", "ودي وأخوي", "دعوة لفعالية"])
            
            if st.button("صياغة وإرسال عبر واتساب"):
                with st.spinner("جاري الصياغة..."):
                    time.sleep(1)
                    if "رسمي" in msg_style:
                        message = f"سعادة الأستاذ {selected_parent} المحترم، نتقدم لكم بخالص الشكر على تعاونكم المستمر معنا في {parent_info['participation_type']}."
                    elif "ودي" in msg_style:
                        message = f"الأخ العزيز {selected_parent}، تحية طيبة وبعد.. حابين نشكرك على وقفتك معانا وجهودك في {parent_info['participation_type']}."
                    else:
                        message = f"نتشرف بدعوتك الأستاذ {selected_parent} لحضور فعاليتنا القادمة، تقديراً لدورك كشريك نجاح في {parent_info['participation_type']}."
                    
                    st.info(f"**الرسالة المقترحة:**\n\n{message}")
                    
                    if parent_info.get('phone'):
                        clean_p = ''.join(filter(str.isdigit, str(parent_info['phone'])))
                        wa_url = f"https://api.whatsapp.com/send?phone={clean_p}&text={message.replace(' ', '%20')}"
                        st.markdown(f"### [🚀 إرسال الآن عبر واتساب]({wa_url})")
                    else:
                        st.error("لا يوجد رقم هاتف مسجل لهذا الشريك")

elif menu == "📈 التقارير والإحصائيات":
    st.title("📈 التقارير والتحليلات الشاملة")
    df_p = load_data("parents")
    df_pl = load_data("action_plan")
    df_e = load_data("events")
    
    if df_pl.empty and df_p.empty:
        st.warning("لا توجد بيانات كافية لتوليد التقارير")
    else:
        # إحصائيات سريعة
        c1, c2, c3 = st.columns(3)
        c1.metric("إجمالي الشركاء", len(df_p))
        c2.metric("إجمالي الفعاليات", len(df_e))
        c3.metric("نسبة الإنجاز", f"{(len(df_pl[df_pl['status'] == 'مكتمل'])/len(df_pl)*100 if not df_pl.empty else 0):.1f}%")

        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("📊 توزيع الشركاء حسب التفاعل")
            if not df_p.empty:
                st.plotly_chart(px.bar(df_p, x='interaction_level', color='participation_type', title="التفاعل حسب مجال الشراكة"), use_container_width=True)
        
        with col_b:
            st.subheader("📅 الجدول الزمني للفعاليات")
            if not df_e.empty:
                st.plotly_chart(px.scatter(df_e, x='date', y='name', size='attendees_count', color='attendees_count', title="الفعاليات وحجم الحضور"), use_container_width=True)

        st.subheader("📋 حالة مهام الخطة السنوية")
        if not df_pl.empty:
            st.plotly_chart(px.pie(df_pl, names='status', hole=0.5, color='status', 
                                   color_discrete_map={'مكتمل':'#27ae60', 'قيد التنفيذ':'#f1c40f', 'متأخر':'#e74c3c'}), use_container_width=True)

# إضافة تذييل الصفحة
st.sidebar.markdown("---")
st.sidebar.caption("v2.0.0 | نظام محلي آمن")
