import streamlit as st
import pandas as pd
import requests
import io

# הגדרות עמוד ועיצוב RTL
st.set_page_config(layout="wide", page_title="קטלוג קורסי בחירה")

# עיצוב מותאם אישית לכרטיסים (CSS)
st.markdown("""
    <style>
    .main { direction: RTL; text-align: right; }
    .course-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
        height: 100%;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .course-title { color: #1E3A8A; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    .course-detail { font-size: 14px; margin-bottom: 5px; }
    .label { font-weight: bold; color: #555; }
    </style>
    """, unsafe_allow_html=True)

SHEET_ID = "1SzycxMz3iO9_5uRTKilDzkRHcI12Mk2flpwe3t2va2w"
COURSES_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=60) # עדכון פעם בדקה
def load_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            return df
        return None
    except:
        return None

st.title("📚 קטלוג קורסי בחירה - תצוגת גלריה")

df = load_data(COURSES_URL)

if df is not None and not df.empty:
    # יצירת רשת (Grid) של 3 עמודות
    cols_per_row = 3
    for i in range(0, len(df), cols_per_row):
        columns = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(df):
                row = df.iloc[i + j]
                with columns[j]:
                    # יצירת הכרטיס עם כל הנתונים מהגיליון
                    st.markdown(f"""
                        <div class="course-card">
                            <div class="course-title">{row.get('שם קורס', 'ללא שם')}</div>
                            <div class="course-detail"><span class="label">🔢 מספר קורס:</span> {row.get('מספר קורס', '-')}</div>
                            <div class="course-detail"><span class="label">👨‍🏫 מרצה:</span> {row.get('מרצה', '-')}</div>
                            <div class="course-detail"><span class="label">🏷️ סיווג:</span> {row.get('סיווג קורס', '-')}</div>
                            <div class="course-detail"><span class="label">🎯 מסלול:</span> {row.get('מסלול', '-')}</div>
                            <div class="course-detail"><span class="label">📝 סוג מבחן:</span> {row.get('סוג מבחן', '-')}</div>
                            <div class="course-detail"><span class="label">📊 הרכב ציון:</span> {row.get('הרכב ציון', '-')}</div>
                            <div class="course-detail"><span class="label">🛡️ דרישות קדם:</span> {row.get('דרישות קדם', '-')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # הוספת כפתור קישור לסילבוס אם קיים
                    syllabus_link = row.get('קישור לסילבוס')
                    if pd.notna(syllabus_link) and str(syllabus_link).startswith('http'):
                        st.link_button("🔗 לצפייה בסילבוס", syllabus_link)
else:
    st.info("טוען נתונים מהגיליון... וודאי שיש נתונים בטאב 'נתוני קורס מוסכמים'.")
