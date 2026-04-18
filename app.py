import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(layout="wide", page_title="מערכת חוות דעת")

# עיצוב RTL לעברית
st.markdown("""<style> .main { direction: RTL; text-align: right; } div.stSelectbox { direction: RTL; } 
.stMarkdown { text-align: right; } .stAlert { direction: RTL; } </style>""", unsafe_allow_html=True)

# המזהה החדש ששלחת
SHEET_ID = "1SzycxMz3iO9_5uRTKilDzkRHcI12Mk2flpwe3t2va2w"

# קישורים בפורמט ייצוא CSV שעוקף חסימות ארגוניות
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
REVIEWS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=1227038165" # ודאי שזה ה-GID של הלשונית השנייה

@st.cache_data(ttl=5)
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        else:
            return None
    except:
        return None

st.title("📚 מדריך הקורסים וחוות דעת")

df_courses = load_data(COURSES_URL)
df_reviews = load_data(REVIEWS_URL)

if df_courses is not None and not df_courses.empty:
    # וידוא שמות העמודות (אם בגיליון כתוב "שם קורס")
    course_col = 'שם קורס' if 'שם קורס' in df_courses.columns else df_courses.columns[0]
    course_list = df_courses[course_col].unique()
    
    selected_course = st.selectbox("בחר קורס כדי לראות פרטים:", course_list)

    if selected_course:
        course_info = df_courses[df_courses[course_col] == selected_course].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**👨‍🏫 מרצה:** {course_info.get('מרצה', 'אין מידע')}")
        with col2:
            st.info(f"**📝 סוג מבחן:** {course_info.get('סוג מבחן', 'אין מידע')}")

        st.divider()
        st.subheader(f"💬 חוות דעת")
        
        if df_reviews is not None and not df_reviews.empty:
            # סינון לפי שם קורס בלשונית חוות דעת
            rev_course_col = 'שם קורס' if 'שם קורס' in df_reviews.columns else df_reviews.columns[0]
            rev_text_col = 'הוספת חוות דעת על קורס' if 'הוספת חוות דעת על קורס' in df_reviews.columns else df_reviews.columns[-1]
            
            revs = df_reviews[df_reviews[rev_course_col] == selected_course]
            if not revs.empty:
                for msg in revs[rev_text_col]:
                    if pd.notna(msg): st.chat_message("user").write(msg)
            else:
                st.write("אין עדיין חוות דעת לקורס זה.")
        
        st.divider()
        with st.form("add_review", clear_on_submit=True):
            new_rev = st.text_area("הוסיפו חוות דעת משלכם:")
            if st.form_submit_button("שלח"):
                # קישור לפורם שלך
                f_url = "https://docs.google.com/forms/d/e/1FAIpQLSdj9u_PAjRucYSvs47vTALbK50ArhouzTbDY08KUCJTA7duAg/formResponse"
                payload = {"entry.1554988012": selected_course, "entry.1706853258": new_rev}
                requests.post(f_url, data=payload)
                st.success("נשלח בהצלחה! המידע יתעדכן תוך מספר רגעים.")
                st.balloons()
else:
    st.warning("לא נמצאו נתונים בגיליון. וודאי שיש לפחות שורה אחת של תוכן מתחת לכותרות.")
