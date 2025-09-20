import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# جلب جدول الدوري من BBC
def fetch_bbc_table():
    url = "https://www.bbc.com/sport/football/premier-league/table"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = []
    rows = soup.select("table.gs-o-table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 10:
            table.append([
                cols[0].text.strip(),  # Pos
                cols[1].text.strip(),  # Team
                cols[2].text.strip(),  # P
                cols[3].text.strip(),  # W
                cols[4].text.strip(),  # D
                cols[5].text.strip(),  # L
                cols[6].text.strip(),  # GF
                cols[7].text.strip(),  # GA
                cols[8].text.strip(),  # GD
                cols[9].text.strip()   # Pts
            ])

    return pd.DataFrame(table, columns=["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"])

# جلب جدول الدوري من Sky
def fetch_sky_table():
    url = "https://www.skysports.com/premier-league-table"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = []
    rows = soup.select("table.standing-table__table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 10:
            table.append([
                cols[0].text.strip(),
                cols[1].text.strip(),
                cols[2].text.strip(),
                cols[3].text.strip(),
                cols[4].text.strip(),
                cols[5].text.strip(),
                cols[6].text.strip(),
                cols[7].text.strip(),
                cols[8].text.strip(),
                cols[9].text.strip()
            ])

    return pd.DataFrame(table, columns=["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"])


# ✅ واجهة Streamlit
st.title("📊 Premier League Standings")

# زر الاختيار بين BBC و Sky
source = st.radio("اختر المصدر:", ["BBC Sport", "Sky Sports"])

try:
    if source == "BBC Sport":
        df = fetch_bbc_table()
    else:
        df = fetch_sky_table()

    st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"⚠️ حصل خطأ أثناء جلب البيانات: {e}")
