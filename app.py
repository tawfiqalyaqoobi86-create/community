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
    # عرض معلومات الربط للتأكد (اختياري)
    with st.sidebar.expander("🔍 حالة الربط السحابي"):
        st.write(f"المستهدف: {st.secrets.connections.gsheets.spreadsheet}")
        if st.button("تحديث البيانات من السحاب"):
            st.cache_data.clear()
            st.rerun()
except Exception as e:
    st.sidebar.warning("لم يتم تفعيل الربط السحابي بـ Google Sheets بعد.")
    conn_gs = None

# تنسيق CSS مخصص للغة العربية والواجهة العصرية
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Almarai:wght@400;700&display=swap');
    
    /* الأساسيات */
    html, body, [class*="css"] {
        font-family: 'Cairo', 'Almarai', sans-serif;
        direction: RTL;
        text-align: right;
    }
    
    /* خلفية الصفحة */
    .stApp {
        background-color: #f8faff;
    }

    /* تصميم البطاقات للمقاييس */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        color: #1e40af !important;
        font-weight: 800 !important;
    }
    
    div[data-testid="metric-container"] {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        border-right: 6px solid #3b82f6;
    }

    /* الأزرار العصرية */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 12px;
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.3);
    }

    /* القائمة الجانبية العصرية */
    section[data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {
        color: white !important;
    }
    
    /* تعديل نصوص الراديو في القائمة الجانبية */
    div[data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        padding: 8px 12px !important;
        border-radius: 10px !important;
        margin-bottom: 5px !important;
    }

    /* تأثيرات متقدمة لتبويبات التنقل */
    div[data-testid="stSidebarNav"] li {
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin: 5px 10px !important;
        border-radius: 12px !important;
    }

    div[data-testid="stSidebarNav"] li:hover {
        background-color: rgba(59, 130, 246, 0.2) !important;
        transform: scale(1.05) translateX(-8px) !important;
        box-shadow: -5px 0px 15px rgba(59, 130, 246, 0.3) !important;
    }

    /* تمييز الرابط النشط */
    div[data-testid="stSidebarNav"] li[aria-selected="true"] {
        background-color: #1e40af !important;
        border-right: 5px solid #60a5fa !important;
    }

    /* العناوين */
    h1 { 
        color: #1e3a8a; 
        font-weight: 800; 
        border-right: 10px solid #3b82f6; 
        padding-right: 20px;
        margin-bottom: 25px;
    }
    h2, h3 { color: #1e40af; font-weight: 700; }

    /* تحسين شكل الجداول */
    .stDataFrame {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# إضافة التاريخ والساعة الحالية (توقيت سلطنة عمان UTC+4)
local_now = datetime.utcnow() + timedelta(hours=4)
st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 10px; border-bottom: 1px solid #334155; margin-bottom: 20px;">
        <p style="color: #60a5fa; margin: 0; font-size: 1.5rem; font-weight: 700;">🕒 {local_now.strftime('%I:%M %p')}</p>
        <p style="color: #94a3b8; margin: 0; font-size: 0.8rem;">📅 {local_now.strftime('%Y-%m-%d')}</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "انتقل إلى:",
    ["لوحة التحكم", "قاعدة بيانات أولياء الأمور", "خطة العمل", "إدارة المبادرات", "الذكاء الاصطناعي", "التقارير والإحصائيات"]
)

# إضافة التوقيع في أسفل القائمة الجانبية
st.sidebar.markdown("---")
st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px;">
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 15px; border-radius: 15px; border: 1px solid #334155;">
            <p style="color: #94a3b8; font-size: 0.7rem; margin-bottom: 5px; letter-spacing: 1px;">تطوير وإخراج</p>
            <p style="color: #3b82f6; font-size: 1.1rem; font-weight: 800; margin: 0; text-shadow: 0 0 10px rgba(59, 130, 246, 0.3);">توفيق اليعقوبي</p>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- وظائف مساعدة ---
def load_data(table):
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

# --- 1. لوحة التحكم ---
if menu == "لوحة التحكم":
    st.title("📊 لوحة القيادة المجتمعية")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("أولياء الأمور الفاعلين", len(load_data("parents")))
    with col2:
        st.metric("المبادرات المنفذة", len(load_data("initiatives")))
    with col3:
        st.metric("الأهداف المكتملة", len(load_data("action_plan")[load_data("action_plan")['status'] == 'مكتمل']))
    with col4:
        st.metric("متوسط أثر المبادرات", f"{load_data('initiatives')['impact_score'].mean():.1f}/10" if not load_data('initiatives').empty else "0/10")

    st.info("مرحباً بك في نظام المساعد الرقمي. يمكنك البدء بإضافة البيانات في التبويبات الجانبية.")

# --- 2. قاعدة بيانات أولياء الأمور ---
elif menu == "قاعدة بيانات أولياء الأمور":
    st.title("👨‍👩‍👧‍👦 قاعدة بيانات أولياء الأمور الفاعلين")
    
    with st.expander("➕ إضافة ولي أمر جديد"):
        with st.form("parent_form"):
            name = st.text_input("الاسم الكامل")
            p_type = st.selectbox("نوع المشاركة", ["دعم تعليمي", "دعم مالي", "خبرات مهنية", "تطوع", "مبادرات"])
            level = st.select_slider("مستوى التفاعل", options=["محدود", "متوسط", "مرتفع"])
            exp = st.text_input("المجال / الخبرة")
            submitted = st.form_submit_button("حفظ البيانات")
            
            if submitted:
                # حفظ محلي
                conn = get_connection()
                conn.execute("INSERT INTO parents (name, participation_type, interaction_level, expertise) VALUES (?, ?, ?, ?)",
                             (name, p_type, level, exp))
                conn.commit()
                conn.close()
                
                # حفظ سحابي (Google Sheets)
                if conn_gs:
                    try:
                        new_row = {"الاسم": name, "النوع": p_type, "التفاعل": level, "الخبرة": exp, "التاريخ": str(datetime.now())}
                        try:
                            # استخدام ttl=0 لضمان قراءة أحدث البيانات وعدم استخدام الكاش
                            df_gs = conn_gs.read(worksheet="Parents", ttl=0)
                            df_updated = pd.concat([df_gs, pd.DataFrame([new_row])], ignore_index=True)
                        except:
                            df_updated = pd.DataFrame([new_row])
                        
                        conn_gs.update(worksheet="Parents", data=df_updated)
                        st.success("✅ تم التحديث في Google Sheets (Parents)")
                    except Exception as e:
                        st.error(f"❌ فشل الحفظ السحابي: {str(e)}")
                
                st.success("تم الحفظ في قاعدة البيانات المحلية")

    df_parents = load_data("parents")

    # زر المزامنة اليدوية للكل
    if not df_parents.empty:
        if st.button("🔄 رفع كافة بيانات أولياء الأمور للسحاب", key="sync_parents_all"):
            if conn_gs:
                try:
                    df_to_sync = df_parents.drop(columns=['id']) if 'id' in df_parents.columns else df_parents
                    conn_gs.update(worksheet="Parents", data=df_to_sync)
                    st.success("✅ تمت مزامنة كافة البيانات مع Google Sheets")
                except Exception as e:
                    st.error(f"❌ فشل المزامنة: {str(e)}")

    if not df_parents.empty:
        st.subheader("🗑️ إدارة البيانات (تعديل/حذف)")
        # استخدام st.data_editor للسماح بالاختيار
        df_parents['إجراء'] = False
        edited_df = st.data_editor(
            df_parents,
            column_config={"إجراء": st.column_config.CheckboxColumn("حذف؟", default=False)},
            disabled=[col for col in df_parents.columns if col != "إجراء"],
            use_container_width=True,
            key="parents_editor"
        )
        
        if st.button("🔴 تنفيذ حذف المحددين", key="del_parents"):
            to_delete = edited_df[edited_df['إجراء'] == True]
            if not to_delete.empty:
                ids = to_delete['id'].tolist()
                conn = get_connection()
                for record_id in ids:
                    conn.execute(f"DELETE FROM parents WHERE id = {record_id}")
                conn.commit()
                conn.close()
                
                # تحديث جوجل شيت (إعادة كتابة البيانات بالكامل بدون المحذوفين)
                if conn_gs:
                    try:
                        # جلب البيانات المتبقية بعد الحذف
                        df_remaining = load_data("parents")
                        # تحويل التنسيق ليتناسب مع شيت (اختياري: يمكنك تنظيف الأعمدة هنا)
                        df_remaining_gs = df_remaining.drop(columns=['id']) if 'id' in df_remaining.columns else df_remaining
                        conn_gs.update(worksheet="Parents", data=df_remaining_gs)
                        st.success("✅ تم الحذف من قاعدة البيانات و Google Sheets")
                    except Exception as e:
                        st.error(f"⚠️ تم الحذف محلياً ولكن فشل التحديث السحابي: {str(e)}")
                
                st.rerun()
    else:
        st.info("لا توجد بيانات حالياً.")

# --- 3. خطة العمل ---
elif menu == "خطة العمل":
    st.title("📅 خطة عمل فريق تنمية العلاقات")
    
    with st.expander("📝 إضافة هدف/نشاط جديد"):
        with st.form("plan_form"):
            obj = st.text_area("الهدف الإجرائي")
            act = st.text_input("النشاط/المبادرة")
            resp = st.text_input("المسؤول")
            time = st.text_input("الجدول الزمني")
            kpi = st.text_input("مؤشر الأداء (KPI)")
            prio = st.selectbox("الأولوية", ["مرتفع", "متوسط", "منخفض"])
            submitted = st.form_submit_button("إضافة للخطة")
            
            if submitted:
                conn = get_connection()
                conn.execute("INSERT INTO action_plan (objective, activity, responsibility, timeframe, kpi, priority) VALUES (?, ?, ?, ?, ?, ?)",
                             (obj, act, resp, time, kpi, prio))
                conn.commit()
                conn.close()
                
                # حفظ سحابي (Google Sheets)
                if conn_gs:
                    try:
                        new_row = {
                            "الهدف": obj, 
                            "النشاط": act, 
                            "المسؤول": resp, 
                            "الزمن": time, 
                            "KPI": kpi, 
                            "الأولوية": prio,
                            "التاريخ": str(datetime.now())
                        }
                        try:
                            df_gs = conn_gs.read(worksheet="ActionPlan", ttl=0)
                            df_updated = pd.concat([df_gs, pd.DataFrame([new_row])], ignore_index=True)
                        except:
                            df_updated = pd.DataFrame([new_row])
                        
                        conn_gs.update(worksheet="ActionPlan", data=df_updated)
                        st.success("✅ تم المزامنة مع Google Sheets (ActionPlan)")
                    except Exception as e:
                        st.error(f"❌ فشل المزامنة السحابية (ActionPlan): {str(e)}")
                
                st.success("تم تحديث الخطة محلياً")

    df_plan = load_data("action_plan")
    
    # زر المزامنة اليدوية للكل
    if not df_plan.empty:
        if st.button("🔄 رفع كافة بيانات الخطة للسحاب", key="sync_plan_all"):
            if conn_gs:
                try:
                    df_to_sync = df_plan.drop(columns=['id']) if 'id' in df_plan.columns else df_plan
                    conn_gs.update(worksheet="ActionPlan", data=df_to_sync)
                    st.success("✅ تمت مزامنة كافة بيانات الخطة مع Google Sheets")
                except Exception as e:
                    st.error(f"❌ فشل المزامنة: {str(e)}")
            else:
                st.warning("الربط السحابي غير مفعل.")

    if not df_plan.empty:
        st.subheader("🗑️ إدارة خطة العمل")
        df_plan['إجراء'] = False
        edited_df = st.data_editor(
            df_plan,
            column_config={"إجراء": st.column_config.CheckboxColumn("حذف؟", default=False)},
            disabled=[col for col in df_plan.columns if col != "إجراء"],
            use_container_width=True,
            key="plan_editor"
        )
        
        if st.button("🔴 حذف الأهداف المختارة", key="del_plan"):
            to_delete = edited_df[edited_df['إجراء'] == True]
            if not to_delete.empty:
                ids = to_delete['id'].tolist()
                conn = get_connection()
                for record_id in ids:
                    conn.execute(f"DELETE FROM action_plan WHERE id = {record_id}")
                conn.commit()
                conn.close()
                
                if conn_gs:
                    try:
                        df_remaining = load_data("action_plan")
                        df_remaining_gs = df_remaining.drop(columns=['id']) if 'id' in df_remaining.columns else df_remaining
                        conn_gs.update(worksheet="ActionPlan", data=df_remaining_gs)
                        st.success("✅ تم تحديث Google Sheets")
                    except Exception as e:
                        st.error(f"❌ فشل تحديث السحاب: {str(e)}")
                st.rerun()
    else:
        st.info("الخطة فارغة حالياً.")

# --- 4. إدارة المبادرات ---
elif menu == "إدارة المبادرات":
    st.title("💡 المبادرات المجتمعية")
    
    with st.expander("🚀 توثيق مبادرة جديدة"):
        with st.form("init_form"):
            title = st.text_input("عنوان المبادرة")
            cat = st.selectbox("المجال", ["تعليمي", "اجتماعي", "مهني", "صحي", "ثقافي"])
            target = st.text_input("الفئة المستهدفة")
            score = st.slider("مستوى الأثر المتوقع (1-10)", 1, 10, 5)
            outcomes = st.text_area("المخرجات والنتائج")
            submitted = st.form_submit_button("توثيق المبادرة")
            
            if submitted:
                conn = get_connection()
                conn.execute("INSERT INTO initiatives (title, category, target_group, impact_score, outcomes, date) VALUES (?, ?, ?, ?, ?, ?)",
                             (title, cat, target, score, outcomes, datetime.now().date()))
                conn.commit()
                conn.close()

                # حفظ سحابي (Google Sheets)
                if conn_gs:
                    try:
                        new_row = {
                            "العنوان": title, 
                            "المجال": cat, 
                            "الفئة": target, 
                            "الأثر": score, 
                            "المخرجات": outcomes, 
                            "التاريخ": str(datetime.now().date())
                        }
                        try:
                            df_gs = conn_gs.read(worksheet="Initiatives", ttl=0)
                            df_updated = pd.concat([df_gs, pd.DataFrame([new_row])], ignore_index=True)
                        except:
                            df_updated = pd.DataFrame([new_row])
                        
                        conn_gs.update(worksheet="Initiatives", data=df_updated)
                        st.success("✅ تم المزامنة مع Google Sheets (Initiatives)")
                    except Exception as e:
                        st.error(f"❌ فشل المزامنة السحابية (Initiatives): {str(e)}")

                st.success("تم توثيق المبادرة بنجاح محلياً")

    df_init = load_data("initiatives")

    # زر المزامنة اليدوية للكل
    if not df_init.empty:
        if st.button("🔄 رفع كافة المبادرات للسحاب", key="sync_init_all"):
            if conn_gs:
                try:
                    df_to_sync = df_init.drop(columns=['id']) if 'id' in df_init.columns else df_init
                    conn_gs.update(worksheet="Initiatives", data=df_to_sync)
                    st.success("✅ تمت مزامنة كافة المبادرات مع Google Sheets")
                except Exception as e:
                    st.error(f"❌ فشل المزامنة: {str(e)}")

    if not df_init.empty:
        st.subheader("🗑️ إدارة المبادرات")
        df_init['إجراء'] = False
        edited_df = st.data_editor(
            df_init,
            column_config={"إجراء": st.column_config.CheckboxColumn("حذف؟", default=False)},
            disabled=[col for col in df_init.columns if col != "إجراء"],
            use_container_width=True,
            key="init_editor"
        )
        
        if st.button("🔴 حذف المبادرات المختارة", key="del_init"):
            to_delete = edited_df[edited_df['إجراء'] == True]
            if not to_delete.empty:
                ids = to_delete['id'].tolist()
                conn = get_connection()
                for record_id in ids:
                    conn.execute(f"DELETE FROM initiatives WHERE id = {record_id}")
                conn.commit()
                conn.close()
                
                if conn_gs:
                    try:
                        df_remaining = load_data("initiatives")
                        df_remaining_gs = df_remaining.drop(columns=['id']) if 'id' in df_remaining.columns else df_remaining
                        conn_gs.update(worksheet="Initiatives", data=df_remaining_gs)
                        st.success("✅ تم تحديث Google Sheets")
                    except Exception as e:
                        st.error(f"❌ فشل تحديث السحاب: {str(e)}")
                st.rerun()
    else:
        st.info("لا توجد مبادرات موثقة.")

# --- 5. الذكاء الاصطناعي (التبويب الذكي) ---
elif menu == "الذكاء الاصطناعي":
    st.title("🤖 مساعد الذكاء الاصطناعي")
    
    parents = load_data("parents")
    inits = load_data("initiatives")
    
    st.subheader("💡 توصيات ذكية لتطوير الشراكة")
    
    if parents.empty:
        st.warning("يرجى إضافة بيانات أولياء الأمور أولاً للحصول على توصيات.")
    else:
        # منطق ذكي بسيط لمحاكاة الـ AI بناءً على البيانات
        high_interact = len(parents[parents['interaction_level'] == 'مرتفع'])
        total = len(parents)
        engagement_rate = (high_interact / total) * 100
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📈 نسبة التفاعل المرتفع: {engagement_rate:.1f}%")
            if engagement_rate < 30:
                st.write("⚠️ **توصية:** اقترح تنظيم 'لقاء قهوة صباحي' غير رسمي لكسر الحاجز مع أولياء الأمور ذوي التفاعل المحدود.")
            else:
                st.write("✅ **توصية:** استثمر في أولياء الأمور الفاعلين لقيادة لجان تطوعية جديدة.")
        
        with col2:
            top_expertise = parents['participation_type'].value_counts().idxmax()
            st.success(f"🌟 القوة الكبرى: {top_expertise}")
            st.write(f"نقترح إطلاق مبادرة في مجال '{top_expertise}' لتعظيم الاستفادة من خبرات المجتمع.")

        st.divider()
        st.subheader("📝 توليد مسودة مبادرة جديدة")
        need = st.text_input("ما هو التحدي الحالي في المدرسة؟ (مثلاً: ضعف القراءة، التنمر)")
        if st.button("توليد مقترح مبادرة"):
            st.write(f"### مقترح مبادرة: 'معاً لنتخطى {need}'")
            st.write(f"**الهدف:** إشراك أولياء الأمور في حل مشكلة {need} عبر ورش عمل تخصصية.")
            st.write("**الأنشطة المقترحة:** لقاءات شهرية + كتيب إرشادي + مسابقة مجتمعية.")

# --- 6. التقارير والإحصائيات ---
elif menu == "التقارير والإحصائيات":
    st.title("📈 التحليلات والتقارير الذكية")
    
    inits = load_data("initiatives")
    if not inits.empty:
        fig = px.pie(inits, names='category', title='توزيع المبادرات حسب المجال', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = px.bar(inits, x='title', y='impact_score', color='category', title='مستوى أثر المبادرات المنفذة')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("لا توجد بيانات كافية لعرض الرسوم البيانية.")

    if st.button("📄 توليد وحفظ تقرير رسمي"):
        report_text = f"""
        تقرير دوري: مشرف تنمية العلاقات المجتمعية
        التاريخ: {datetime.now().date()}
        ------------------------------------------
        1. ملخص الإنجاز: تم تنفيذ {len(inits)} مبادرة.
        2. حالة أولياء الأمور: يوجد {len(load_data('parents'))} ولي أمر مسجل.
        3. التوصيات: الاستمرار في تعزيز التواصل الرقمي.
        ------------------------------------------
        """
        st.text_area("التقرير الرسمي", report_text)

        # حفظ سحابي للتقارير
        if conn_gs:
            try:
                new_row = {"التاريخ": str(datetime.now()), "محتوى التقرير": report_text}
                try:
                    df_gs = conn_gs.read(worksheet="Reports", ttl=0)
                    df_updated = pd.concat([df_gs, pd.DataFrame([new_row])], ignore_index=True)
                except:
                    df_updated = pd.DataFrame([new_row])
                
                conn_gs.update(worksheet="Reports", data=df_updated)
                st.success("✅ تم حفظ التقرير في Google Sheets (Reports)")
            except Exception as e:
                st.error(f"❌ فشل حفظ التقرير سحابياً: {str(e)}")
