import streamlit as st
import pandas as pd
import requests
import io

# הגדרות עמוד
st.set_page_config(layout="wide", page_title="קטלוג קורסי בחירה", initial_sidebar_state="collapsed")

# עיצוב RTL, הסתרת תפריטים ויישור גובה הכרטיסים
st.markdown("""
    <style>
    .main { direction: RTL; text-align: right; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* עיצוב הכרטיס עם גובה קבוע */
    div.stButton > button {
        width: 100%;
        height: 180px; /* גובה קבוע לכל הכרטיסים */
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        background-color: white;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center; /* מרכז את הטקסט אנכית */
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        white-space: normal; /* מאפשר ירידת שורה בטקסט */
        line-height: 1.4;
    }
    
    div.stButton > button:hover {
        border-color: #1E3A8A;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    /* התאמת פונט בתוך הכפתור */
    div.stButton > button p {
        font-size: 18px;
        font-weight: bold;
        color: #1E3A8A;
        margin: 0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# פונקציית החלונית הקופצת (נשארת ללא שינוי)
@st.dialog("פרטי קורס מלאים")
def show_course_details(row, df_reviews):
    course_name = row.get('שם קורס', 'ללא שם')
    st.subheader(f"📚 {course_name}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**🔢 מספר קורס:** {row.get('מספר קורס', '-')}")
        st.write(f"**👨‍🏫 מרצה:** {row.get('מרצה', '-')}")
        st.write(f"**🏷️ סיווג:** {row.get('סיווג קורס', '-')}")
    with col2:
        st.write(f"**🎯 מסלול:** {row.get('מסלול', '-')}")
        st.write(f"**📝 סוג מבחן:** {row.get('סוג מבחן', '-')}")
        st.write(f"**📊 הרכב ציון:** {row.get('הרכב ציון', '-')}")
    
    st.write(f"**🛡️ דרישות קדם:** {row.get('דרישות קדם', '-')}")
    
    syllabus = row.get('קישור לסילבוס')
    if pd.notna(syllabus) and str(syllabus).startswith('http'):
        st.link_button("🔗 צפייה בסילבוס המלא", syllabus, use_container_width=True)
    
    st.divider()
    st.subheader("💬 חוות דעת סטודנטים")
    if df_reviews is not None:
        relevant = df_reviews[df_reviews['שם קורס'] == course_name]
        if not relevant.empty:
            for msg in relevant['הוספת חוות דעת על קורס']:
                if pd.notna(msg): st.chat_message("user").write(msg)
        else:
            st.info("אין עדיין חוות דעת לקורס זה.")
    
    st.divider()
    with st.expander("✍️ הוספת חוות דעת חדשה"):
        with st.form("modal_form", clear_on_submit=True):
            user_text = st.text_area("החוות דעת שלך:")
            if st.form_submit_button("שלח חוות דעת"):
                form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdj9u_PAjRucYSvs47vTALbK50ArhouzTbDY08KUCJTA7duAg/formResponse"
                payload = {"entry.1554988012": course_name, "entry.1706853258": user_text}
                requests.post(form_url, data=payload)
                st.success("נשלח! המידע יתעדכן בקרוב.")

# טעינת נתונים
SHEET_ID = "1SzycxMz3iO9_5uRTKilDzkRHcI12Mk2flpwe3t2va2w"
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
REVIEWS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=318705122"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        response = requests.get(url)
        return pd.read_csv(io.StringIO(response.content.decode('utf-8'))) if response.status_code == 200 else None
    except: return None

st.title("🎓 קטלוג קורסי בחירה")
st.write("לחצו על כרטיס קורס לצפייה בפרטים והוספת חוות דעת")

df_courses = load_data(COURSES_URL)
df_reviews = load_data(REVIEWS_URL)

if df_courses is not None and not df_courses.empty:
    # יצירת גריד אחיד
    cols = st.columns(3)
    for idx, row in df_courses.iterrows():
        with cols[idx % 3]:
            # בניית טקסט הכרטיס בצורה נקייה
            name = row.get('שם קורס', 'ללא שם')
            lecturer = row.get('מרצה', '-')
            c_num = row.get('מספר קורס', '-')
            
            # הצגת הכפתור/כרטיס
            if st.button(f"{name}\n{lecturer}\n{c_num}", key=f"btn_{idx}"):
                show_course_details(row, df_reviews)
