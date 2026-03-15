import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from io import BytesIO
from googlesearch import search

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Premier League Dashboard", layout="wide", page_icon="⚽")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"}

# --- دوال جلب البيانات ---
@st.cache_data(ttl=3600) # تخزين مؤقت لتسريع التطبيق
def get_table():
    link = "https://onefootball.com/en/competition/premier-league-9/table"
    source = requests.get(link, headers=HEADERS).text
    soup = BeautifulSoup(source, "lxml")
    
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
                "المركز": position_elem.text.strip(),
                "الفريق": team_elem.text.strip(),
                "لعب": stats[2].text.strip(),
                "فاز": stats[3].text.strip(),
                "تعادل": stats[4].text.strip(),
                "خسر": stats[5].text.strip(),
                "فارق الأهداف": stats[6].text.strip(),
                "النقاط": stats[7].text.strip()
            })
    return pd.DataFrame(data)

@st.cache_data(ttl=3600)
def get_fixtures(team_filter=""):
    link = "https://onefootball.com/en/competition/premier-league-9/fixtures"
    source = requests.get(link, headers=HEADERS).text
    page = BeautifulSoup(source, "lxml")
    
    match_pattern = re.compile(r"matchCard", re.IGNORECASE)
    fix_elements = page.find_all("a", class_=match_pattern)
    
    fixtures = [match.get_text(separator=" | ").strip() for match in fix_elements]
    
    if team_filter:
        fixtures = [f for f in fixtures if team_filter.lower() in f.lower()]
    return fixtures

def get_player_stats(player_name):
    query = f"{player_name} premier league.com stats"
    search_results = list(search(query, num_results=3))
    if not search_results:
        return None, "لم يتم العثور على اللاعب."
    
    res = search_results[0]
    if "stats" in res: res = res.replace('stats', 'overview')
    sta = res.replace('overview', 'stats')

    source = requests.get(sta, headers=HEADERS).text
    page = BeautifulSoup(source, "lxml")
    
    name_elem = page.find("div", class_="player-header__name t-colour")
    if not name_elem: return None, "تعذر جلب بيانات هذا اللاعب."
    
    name = re.sub(r'\s+', ' ', name_elem.text).strip()
    
    stats_dict = {"الاسم": name}
    stat_elements = page.find_all("div", class_="player-stats__stat-value")
    for stat in stat_elements:
        title = stat.text.split("\n")[0].strip()
        val_elem = stat.find("span", class_="allStatContainer")
        stats_dict[title] = val_elem.text.strip() if val_elem else "N/A"
        
    return stats_dict, None

# --- واجهة المستخدم (Streamlit UI) ---
st.title("⚽ Premier League Analytics Dashboard")

# تقسيم الواجهة إلى 3 تبويبات
tab1, tab2, tab3 = st.tabs(["📊 الترتيب", "📅 المباريات", "🏃 إحصائيات اللاعبين"])

# التبويب الأول: جدول الترتيب
with tab1:
    st.subheader("جدول ترتيب الدوري الإنجليزي")
    try:
        df_table = get_table()
        st.dataframe(df_table, use_container_width=True)
        
        # أزرار التحميل
        col1, col2 = st.columns(2)
        with col1:
            csv = df_table.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ تحميل CSV", data=csv, file_name="pl_table.csv", mime="text/csv")
    except Exception as e:
        st.error(f"خطأ في جلب الترتيب: {e}")

# التبويب الثاني: المباريات
with tab2:
    st.subheader("المباريات القادمة")
    team_search = st.text_input("🔍 ابحث عن مباريات فريق معين (اختياري):", placeholder="مثال: Arsenal, Chelsea...")
    
    try:
        matches = get_fixtures(team_search)
        if matches:
            for match in matches:
                st.info(match)
        else:
            st.warning("لم يتم العثور على مباريات.")
    except Exception as e:
        st.error(f"خطأ في جلب المباريات: {e}")

# التبويب الثالث: إحصائيات اللاعبين
with tab3:
    st.subheader("محرك بحث إحصائيات اللاعبين")
    player_input = st.text_input("🔍 أدخل اسم اللاعب:", placeholder="مثال: Mohamed Salah, Haaland...")
    
    if st.button("ابحث عن اللاعب"):
        if player_input:
            with st.spinner("جارِ البحث وجلب البيانات..."):
                stats, error = get_player_stats(player_input)
                if error:
                    st.error(error)
                else:
                    st.success(f"تم العثور على بيانات: {stats.get('الاسم')}")
                    
                    # عرض الإحصائيات في شبكة جميلة
                    cols = st.columns(3)
                    idx = 0
                    for key, value in stats.items():
                        if key != "الاسم":
                            cols[idx % 3].metric(label=key, value=value)
                            idx += 1
        else:
            st.warning("الرجاء إدخال اسم اللاعب أولاً.")
