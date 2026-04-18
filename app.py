import streamlit as st
import pandas as pd
import requests

# הגדרות עיצוב ועברית
st.set_page_config(layout="wide", page_title="מידע וחוות דעת על קורסים")
st.markdown("""<style>
    div.stButton > button { width: 100%; border-radius: 5px; background-color: #f0f2f6; }
    .stMarkdown { text-align: right; }
    header {visibility: hidden;}
</style>""", unsafe_allow_html=True)

# קישורים לגיליונות (CSV Export)
SHEET_ID = "1nSKG17zYkHLliAsIcxl9thhMOoHnsnErViH2g6w3po0"
# לשונית נתוני קורסים (נתוני קורס מוסכמים)
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=%D7%A0%D7%AA%D7%95%D7%A0%D7%99%20%D7%A7%D7%95%D7%A8%D7%A1%20%D7%9E%D7%95%D7%A1%D7%9B%D7%9E%D7%99%D7%9D"
# לשונית חוות דעת (איסוף חוות דעת)
REVIEWS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=%D7%90%D7%99%D7%A1%D7%95%D7%A3%20%D7%97%D7%95%D7%95%D7%AA%20%D7%93%D7%A2%D7%AA"

@st.cache_data(ttl=10) # רענון כל 10 שניות כדי לראות תגובות חדשות מיד
def get_data(url):
    return pd.read_csv(url)

# טעינת הנתונים
try:
    df_courses = get_data(COURSES_URL)
    df_reviews = get_data(REVIEWS_URL)
except:
    st.error("לא מצליח להתחבר לגוגל שיטס. וודאי שהשיתוף פתוח ל-Anyone with the link.")
    st.stop()

st.title("📚 מדריך הקורסים וחוות דעת")

# בחירת קורס מתוך הרשימה בגיליון
course_list = df_courses['שם קורס'].unique()
selected_course = st.selectbox("בחר קורס כדי לראות פרטים וחוות דעת:", course_list)

# הצגת מידע על הקורס הנבחר
course_info = df_courses[df_courses['שם קורס'] == selected_course].iloc[0]
col1, col2 = st.columns(2)

with col1:
    st.info(f"**מרצה:** {course_info.get('מרצה', 'אין מידע')}")
    st.info(f"**סוג מבחן:** {course_info.get('סוג מבחן', 'אין מידע')}")
with col2:
    st.info(f"**דרישות קדם:** {course_info.get('דרישות קדם', 'אין מידע')}")
    st.info(f"**הרכב ציון:** {course_info.get('הרכב ציון', 'אין מידע')}")

st.divider()

# הצגת חוות דעת קיימות
st.subheader(f"💬 מה סטודנטים אומרים על {selected_course}:")
relevant_reviews = df_reviews[df_reviews['שם קורס'] == selected_course]

if not relevant_reviews.empty:
    for msg in relevant_reviews['הוספת חוות דעת על קורס']:
        st.chat_message("user").write(msg)
else:
    st.write("עדיין אין חוות דעת לקורס זה. תהיו הראשונים!")

st.divider()

# טופס הוספה פנימי - שולח ל-Google Form מאחורי הקלעים
st.subheader("✍️ הוספת חוות דעת חדשה")
with st.form("new_review", clear_on_submit=True):
    new_content = st.text_area("כתבו כאן את חוות הדעת שלכם (היא תופיע באתר מיד):")
    submitted = st.form_submit_button("שלח חוות דעת")
    
    if submitted and new_content:
        # כאן אנחנו שולחים את המידע לטופס שלך
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdj9u_PAjRucYSvs47vTALbK50ArhouzTbDY08KUCJTA7duAg/formResponse"
        payload = {
            "entry.1554988012": selected_course, # מספר השדה של שם הקורס
            "entry.1706853258": new_content      # מספר השדה של חוות הדעת
        }
        requests.post(form_url, data=payload)
        st.success("תודה! חוות הדעת נשמרה ומסונכרנת.")
        st.balloons()
