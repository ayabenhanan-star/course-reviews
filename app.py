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
    
    /* הגדרות בסיס לכרטיס */
    div.stButton > button {
        width: 100%;
        height: 180px; 
        border-radius: 15px;
        background-color: white;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        white-space: normal;
        line-height: 1.4;
        border: 3px solid #e0e0e0; /* ברירת מחדל */
    }
    
    div.stButton > button:hover {
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }

    div.stButton > button p {
        font-size: 18px;
        font-weight: bold;
        color: #1E3A8A;
        margin: 0;
        text-align: center;
    }

    /* צבעים לפי סיווג - דריסה של ה-border */
    /* ירוק פסטל לליבה */
    div.liba-border > div.stButton > button { border-color: #C1E1C1 !important; }
    /* סגול פסטל לבחירה */
    div.bechira-border > div.stButton > button { border-color: #E6E6FA !important; }
    </style>
    """, unsafe_allow_html=True)

def get_val(row, partial_name):
    for col in row.index:
        if partial_name in col:
            val = row[col]
            return val if pd.notna(val) and str(val).lower() != 'nan' else "-"
    return "-"

@st.dialog("פרטי קורס מלאים")
def show_course_details(row, df_reviews):
    course_name = get_val(row, 'שם קורס')
    st.subheader(f"📚 {course_name}")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**🔢 מספר קורס:** {get_val(row, 'מספר קורס')}")
        st.write(f"**👨‍🏫 מרצה:** {get_val(row, 'מרצה')}")
        st.write(f"**🏷️ סיווג:** {get_val(row, 'סיווג')}")
    with col2:
        st.write(f"**🎯 מסלול:** {get_val(row, 'מסלול')}")
        st.write(f"**📝 סוג מבחן:** {get_val(row, 'סוג מבחן')}")
        st.write(f"**📊 הרכב ציון:** {get_val(row, 'הרכב הציון')}")
    st.write(f"**🛡️ דרישות קדם:** {get_val(row, 'דרישות קדם')}")
    syllabus = get_val(row, 'סילבוס')
    if syllabus != "-" and str(syllabus).startswith('http'):
        st.link_button("🔗 צפייה בסילבוס המלא", syllabus, use_container_width=True)
    st.divider()
    st.subheader("💬 חוות דעת סטודנטים")
    if df_reviews is not None:
        rev_course_col = next((c for c in df_reviews.columns if 'שם קורס' in c), None)
        rev_content_col = next((c for c in df_reviews.columns if 'חוות דעת' in c), None)
        if rev_course_col and rev_content_col:
            relevant = df_reviews[df_reviews[rev_course_col] == course_name]
            if not relevant.empty:
                for msg in relevant[rev_content_col]:
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

SHEET_ID = "1SzycxMz3iO9_5uRTKilDzkRHcI12Mk2flpwe3t2va2w"
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
REVIEWS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=318705122"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        response = requests.get(url)
        return pd.read_csv(io.StringIO(response.content.decode('utf-8'))) if response.status_code == 200 else None
    except: return None

st.title("🎓 ניהול ידע - בחירת קורסים")
df_courses = load_data(COURSES_URL)
df_reviews = load_data(REVIEWS_URL)

if df_courses is not None and not df_courses.empty:
    cols = st.columns(3)
    for idx, row in df_courses.iterrows():
        # זיהוי סיווג לצביעת מסגרת
        sivug = str(get_val(row, 'סיווג'))
        border_class = ""
        if "ליבה" in sivug:
            border_class = "liba-border"
        elif "בחירה" in sivug:
            border_class = "bechira-border"
            
        with cols[idx % 3]:
            # עטיפת הכפתור ב-div עם הקלאס המתאים לצבע
            st.markdown(f'<div class="{border_class}">', unsafe_allow_html=True)
            name = get_val(row, 'שם קורס')
            lecturer = get_val(row, 'מרצה')
            c_num = get_val(row, 'מספר קורס')
            if st.button(f"{name}\n{lecturer}\n{c_num}", key=f"btn_{idx}"):
                show_course_details(row, df_reviews)
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("טוען נתונים...")
