import streamlit as st
import pandas as pd
import requests
import io

# הגדרות עמוד
st.set_page_config(layout="wide", page_title="קטלוג קורסי בחירה")

# עיצוב RTL והסתרת כפתורי GitHub/Streamlit
st.markdown("""
    <style>
    .main { direction: RTL; text-align: right; }
    /* הסתרת כפתור ה-GitHub והתפריט של Streamlit למשתמשים */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .course-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e1e4e8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }
    .course-title { color: #1E3A8A; font-size: 22px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #f0f2f6; padding-bottom: 10px; }
    .label { font-weight: bold; color: #4b5563; }
    .detail-row { margin-bottom: 8px; font-size: 15px; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1SzycxMz3iO9_5uRTKilDzkRHcI12Mk2flpwe3t2va2w"
# טעינת נתונים
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"
REVIEWS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=318705122"

@st.cache_data(ttl=60)
def load_data(url):
    try:
        response = requests.get(url)
        return pd.read_csv(io.StringIO(response.content.decode('utf-8'))) if response.status_code == 200 else None
    except: return None

st.title("📚 קטלוג קורסי בחירה")
st.write("לחצו על 'פרטים נוספים וחוות דעת' בכל קורס כדי לראות את המידע המלא.")

df_courses = load_data(COURSES_URL)
df_reviews = load_data(REVIEWS_URL)

if df_courses is not None and not df_courses.empty:
    cols_per_row = 3
    for i in range(0, len(df_courses), cols_per_row):
        columns = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(df_courses):
                row = df_courses.iloc[i + j]
                with columns[j]:
                    # תצוגת הכרטיס
                    st.markdown(f"""
                        <div class="course-card">
                            <div class="course-title">{row.get('שם קורס', 'ללא שם')}</div>
                            <div class="detail-row"><span class="label">🔢 מספר:</span> {row.get('מספר קורס', '-')}</div>
                            <div class="detail-row"><span class="label">👨‍🏫 מרצה:</span> {row.get('מרצה', '-')}</div>
                            <div class="detail-row"><span class="label">🏷️ סיווג:</span> {row.get('סיווג קורס', '-')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # תיבה נפתחת לפרטים נוספים וחוות דעת
                    with st.expander("🔍 פרטים נוספים וחוות דעת"):
                        st.write(f"**🎯 מסלול:** {row.get('מסלול', '-')}")
                        st.write(f"**📝 סוג מבחן:** {row.get('סוג מבחן', '-')}")
                        st.write(f"**📊 הרכב ציון:** {row.get('הרכב ציון', '-')}")
                        st.write(f"**🛡️ דרישות קדם:** {row.get('דרישות קדם', '-')}")
                        
                        # קישור לסילבוס
                        syllabus = row.get('קישור לסילבוס')
                        if pd.notna(syllabus) and str(syllabus).startswith('http'):
                            st.link_button("🔗 סילבוס הקורס", syllabus)
                        
                        st.divider()
                        st.subheader("💬 חוות דעת")
                        if df_reviews is not None:
                            # סינון חוות דעת לפי שם הקורס
                            course_name = row.get('שם קורס')
                            relevant = df_reviews[df_reviews['שם קורס'] == course_name]
                            if not relevant.empty:
                                for msg in relevant['הוספת חוות דעת על קורס']:
                                    if pd.notna(msg): st.chat_message("user").write(msg)
                            else:
                                st.write("אין עדיין חוות דעת.")
else:
    st.info("טוען נתונים...")
