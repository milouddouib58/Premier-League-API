import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# عنوان الصفحة
st.set_page_config(page_title="Premier League Table", layout="wide")
st.title("📊 Premier League Standings")

# رابط موقع ESPN أو BBC أو Sky Sports (كمثال ESPN)
URL = "https://www.espn.com/soccer/standings/_/league/eng.1"

# جلب البيانات
try:
    response = requests.get(URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # البحث عن الصفوف الخاصة بالجدول
    rows = soup.find_all("tr", class_="Table__TR")

    data = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 9:  # نتأكد أن الصف فيه بيانات كافية
            team = cells[0].text.strip()
            played = cells[1].text.strip()
            wins = cells[2].text.strip()
            draws = cells[3].text.strip()
            losses = cells[4].text.strip()
            gf = cells[5].text.strip()  # Goals For
            ga = cells[6].text.strip()  # Goals Against
            gd = cells[7].text.strip()  # Goal Difference
            points = cells[8].text.strip()

            data.append([team, played, wins, draws, losses, gf, ga, gd, points])

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data, columns=[
        "Team", "Played", "Wins", "Draws", "Losses", "GF", "GA", "GD", "Points"
    ])

    # عرض الجدول
    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ حصل خطأ أثناء جلب البيانات: {e}")
