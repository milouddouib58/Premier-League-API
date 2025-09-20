import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
from io import BytesIO

# ====== دالة تجيب البيانات ======
def get_premier_league_table():
    url = "https://www.skysports.com/premier-league-table"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"class": "standing-table__table"})
    rows = table.find("tbody").find_all("tr")

    data = []
    for row in rows:
        cols = row.find_all("td")
        if cols:
            data.append({
                "Position": cols[0].text.strip(),
                "Team": cols[1].text.strip(),
                "Played": cols[2].text.strip(),
                "Won": cols[3].text.strip(),
                "Drawn": cols[4].text.strip(),
                "Lost": cols[5].text.strip(),
                "GF": cols[6].text.strip(),
                "GA": cols[7].text.strip(),
                "GD": cols[8].text.strip(),
                "Points": cols[9].text.strip()
            })

    return pd.DataFrame(data)


# ====== واجهة Streamlit ======
st.set_page_config(page_title="Premier League Table", layout="wide")
st.title("📊 Premier League Standings (Sky Sports)")

try:
    df = get_premier_league_table()
    st.success("✅ تم جلب البيانات بنجاح!")

    # عرض الجدول
    st.dataframe(df, use_container_width=True)

    # تحميل CSV
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("⬇️ تحميل CSV", data=csv, file_name="premier_league_table.csv", mime="text/csv")

    # تحميل Excel
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("⬇️ تحميل Excel", data=buffer.getvalue(), file_name="premier_league_table.xlsx", mime="application/vnd.ms-excel")

except Exception as e:
    st.error(f"⚠️ حصل خطأ أثناء جلب البيانات: {e}")
