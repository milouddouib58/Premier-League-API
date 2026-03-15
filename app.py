import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from io import BytesIO
import re

def get_premier_league_table():
    link = "https://onefootball.com/en/competition/premier-league-9/table"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # إعداد أنماط بحث مرنة تتجاهل الرموز العشوائية
    row_pattern = re.compile(r"standings__row", re.IGNORECASE)
    cell_pattern = re.compile(r"standings__cell", re.IGNORECASE)
    team_pattern = re.compile(r"standings__teamName", re.IGNORECASE)

    rows = soup.find_all("li", class_=row_pattern)
    
    data = []
    
    for row in rows:
        position_elem = row.find("div", class_=cell_pattern)
        team_elem = row.find(["p", "span", "div"], class_=team_pattern)
        stats = row.find_all("div", class_=cell_pattern)

        if position_elem and team_elem and len(stats) >= 8:
            data.append({
                "Position": position_elem.text.strip(),
                "Team": team_elem.text.strip(),
                "Played": stats[2].text.strip(),
                "Wins": stats[3].text.strip(),
                "Draws": stats[4].text.strip(),
                "Losses": stats[5].text.strip(),
                "Goal Difference": stats[6].text.strip(),
                "Points": stats[7].text.strip()
            })

    if not data:
        raise ValueError("⚠️ لم يتم العثور على بيانات الترتيب. تأكد من اتصال الإنترنت أو هيكلة موقع OneFootball.")

    return pd.DataFrame(data)

# --- Streamlit App ---
st.set_page_config(page_title="Premier League Table", layout="wide")
st.title("📊 Premier League Standings (OneFootball)")

try:
    df = get_premier_league_table()
    
    st.success("✅ تم جلب البيانات بنجاح!")
    st.dataframe(df, use_container_width=True)

    # CSV Download
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ تحميل CSV", data=csv, file_name="premier_league_table.csv", mime="text/csv")

    # Excel Download
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("⬇️ تحميل Excel", data=buffer.getvalue(),
                       file_name="premier_league_table.xlsx",
                       mime="application/vnd.ms-excel")

except Exception as e:
    st.error(f"⚠️ حصل خطأ أثناء جلب البيانات: {e}")
