import streamlit as st
import pandas as pd
import requests

# הגדרות תצוגה ועברית
st.set_page_config(layout="wide", page_title="מערכת חוות דעת על קורסים")

# הזרקת CSS לעיצוב מימין לשמאל (RTL)
st.markdown("""
    <style>
    .main { direction: RTL; text-align: right; }
    div.stSelectbox { direction: RTL; }
    div.stTextArea { direction: RTL; }
    .stMarkdown { text-align: right; }
    .stAlert { direction: RTL; }
    </style>
    """, unsafe_allow_html=True)

# מזהה הגיליון שלך
SHEET_ID = "1nSKG17zYkHLliAsIcxl9thhMOoHnsnErViH2g6w3po0"

# קישורים ישירים ללשוניות בפורמט CSV (כולל קידוד לשמות בעברית)
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=%D7%A0%D7%AA%D7%95%D7%A0%D7%99%20%D7%A7%D7%95%D7%A8%D7%A1%20%D7%9E%D7%95%D7%A1%D7%9B%D7%9E%D7%99%D7%9D"
REVIEWS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=%D7%90%D7%99%D7%A1%D7%95%D7%A3%20%D7%97%D7%95%D7%95%D7%AA%20%D7%93%D7%A2%D7%AA"

@st.cache_data(ttl=10)
def load_data(url):
    return pd.read_csv(url)

# כותרת האפליקציה
st.title("📚 מדריך הקורסים וחוות דעת")

try:
    # טעינת הנתונים
    df_courses = load_data(COURSES_URL)
    df_reviews = load_data(REVIEWS_URL)

    # רשימת קורסים לבחירה
    course_list = df_courses['שם קורס'].unique()
    selected_course = st.selectbox("בחר קורס כדי לראות פרטים וחוות דעת:", course_list)

    if selected_course:
        # סינון מידע על הקורס הנבחר
        course_info = df_courses[df_courses['שם קורס'] == selected_course].iloc[0]
        
        # הצגת פרטי הקורס בתיבות מעוצבות
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**👨‍🏫 מרצה:** {course_info.get('מרצה', 'אין מידע')}")
            st.info(f"**📝 סוג מבחן:** {course_info.get('סוג מבחן', 'אין מידע')}")
        with col2:
            st.info(f"**⚙️ דרישות קדם:** {course_info.get('דרישות קדם', 'אין מידע')}")
            st.info(f"**📊 הרכב ציון:** {course_info.get('הרכב ציון', 'אין מידע')}")

        st.divider()

        # הצגת חוות דעת קיימות
        st.subheader(f"💬 חוות דעת של סטודנטים על {selected_course}")
        relevant_reviews = df_reviews[df_reviews['שם קורס'] == selected_course]

        if not relevant_reviews.empty:
            for msg in relevant_reviews['הוספת חוות דעת על קורס']:
                if pd.notna(msg):
                    st.chat_message("user").write(msg)
        else:
            st.write("עדיין אין חוות דעת לקורס זה. תהיו הראשונים לכתוב!")

        st.divider()

        # טופס הוספת חוות דעת פנימי
        st.subheader("✍️ הוספת חוות דעת חדשה")
        with st.form("review_form", clear_on_submit=True):
            user_review = st.text_area("הזינו את חוות הדעת שלכם כאן (היא תופיע באתר לאחר רענון):")
            submit_button = st.form_submit_button("שלח חוות דעת")

            if submit_button:
                if user_review:
                    # כתובת ה-POST של ה-Google Form שלך
                    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdj9u_PAjRucYSvs47vTALbK50ArhouzTbDY08KUCJTA7duAg/formResponse"
                    
                    # מיפוי השדות (ID של השדות בפורמט של גוגל)
                    payload = {
                        "entry.1554988012": selected_course,
                        "entry.1706853258": user_review
                    }
                    
                    try:
                        requests.post(form_url, data=payload)
                        st.success("תודה! חוות הדעת נשלחה בהצלחה ותופיע באתר תוך מספר רגעים.")
                        st.balloons()
                    except:
                        st.error("הייתה שגיאה בשליחה. אנא נסו שוב מאוחר יותר.")
                else:
                    st.warning("נא לכתוב משהו בתיבת הטקסט לפני השליחה.")

except Exception as e:
    st.error(f"שגיאה בטעינת הנתונים: {e}")
    st.write("וודאי שהגיליון מוגדר כ-'ציבורי' (Anyone with the link) ופורסם לאינטרנט (Publish to web).")
