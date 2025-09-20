import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# إعداد صفحة Streamlit
st.set_page_config(page_title="Premier League Table", layout="wide")
st.title("📊 Premier League Standings")

# رابط ترتيب الدوري من ESPN
URL = "https://www.espn.com/soccer/standings/_/league/eng.1"

# إضافة headers لتفادي خطأ 403
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
}

try:
    response = requests.get(URL, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # البحث عن الصفوف الخاصة بالجدول
    rows = soup.find_all("tr", class_="Table__TR")

    data = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 9:
            team = cells[0].text.strip()
            played = cells[1].text.strip()
            wins = cells[2].text.strip()
            draws = cells[3].text.strip()
            losses = cells[4].text.strip()
            gf = cells[5].text.strip()
            ga = cells[6].text.strip()
            gd = cells[7].text.strip()
            points = cells[8].text.strip()

            data.append([team, played, wins, draws, losses, gf, ga, gd, points])

    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(data, columns=[
        "Team", "Played", "Wins", "Draws", "Losses", "GF", "GA", "GD", "Points"
    ])

    # عرض الجدول
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("⚠️ لم يتم العثور على بيانات من الصفحة.")

except Exception as e:
    st.error(f"⚠️ حصل خطأ أثناء جلب البيانات: {e}")
