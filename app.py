import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from io import BytesIO

def get_premier_league_table():
    url = "https://www.skysports.com/premier-league-table"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"class": "standing-table__table"})
    if not table:
        raise ValueError("لم يتم العثور على جدول الترتيب في الصفحة. تحقق من تغيّر هيكلة الموقع.")

    rows = table.find("tbody").find_all("tr")
    data = []
    for row in rows:
        cols = row.find_all("td")
        if cols:
            data.append({
                "Position": cols[0].get_text(strip=True),
                "Team": cols[1].get_text(strip=True),
                "Played": cols[2].get_text(strip=True),
                "Won": cols[3].get_text(strip=True),
                "Drawn": cols[4].get_text(strip=True),
                "Lost": cols[5].get_text(strip=True),
                "GF": cols[6].get_text(strip=True),
                "GA": cols[7].get_text(strip=True),
                "GD": cols[8].get_text(strip=True),
                "Points": cols[9].get_text(strip=True),
            })

    return pd.DataFrame(data)


# واجهة Streamlit
st.set_page_config(page_title="Premier League Table", layout="wide")
st.title("📊 Premier League Standings (Sky Sports)")

try:
    df = get_premier_league_table()
    st.success("✅ تم جلب البيانات بنجاح!")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ تحميل CSV", data=csv, file_name="premier_league_table.csv", mime="text/csv")

    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("⬇️ تحميل Excel", data=buffer.getvalue(), file_name="premier_league_table.xlsx", mime="application/vnd.ms-excel")

except Exception as e:
    st.error(f"⚠️ حصل خطأ أثناء جلب البيانات: {e}")
