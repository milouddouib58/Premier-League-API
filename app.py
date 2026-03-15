import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from io import BytesIO

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Premier League Dashboard", layout="wide", page_icon="⚽")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

# --- دوال جلب البيانات ---
@st.cache_data(ttl=3600)
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

# دالة سحب بيانات الفانتسي (FPL API) المخزنة مؤقتاً لتسريع البحث
@st.cache_data(ttl=43200) # التحديث كل 12 ساعة
def get_fpl_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_player_stats_fpl(player_name):
    try:
        data = get_fpl_data()
        players = data.get('elements', [])
        # استخراج قواميس الفرق والمراكز لترجمتها
        teams = {t['id']: t['name'] for t in data.get('teams', [])}
        positions = {p['id']: p['singular_name'] for p in data.get('element_types', [])}

        search_name = player_name.lower().strip()
        found_player = None

        # البحث عن اللاعب في قاعدة البيانات
        for p in players:
            full_name = f"{p['first_name']} {p['second_name']}".lower()
            web_name = p['web_name'].lower()
            if search_name in full_name or search_name in web_name:
                found_player = p
                break

        if not found_player:
            return None, f"لم أتمكن من إيجاد اللاعب '{player_name}'. حاول كتابة الاسم الأول أو الأخير فقط."

        # تنسيق الإحصائيات بشكل جميل
        stats_dict = {
            "الاسم": f"{found_player['first_name']} {found_player['second_name']}",
            "الفريق": teams.get(found_player['team'], "غير معروف"),
            "المركز": positions.get(found_player['element_type'], "غير معروف"),
            "الأهداف": str(found_player['goals_scored']),
            "التمريرات الحاسمة (Assists)": str(found_player['assists']),
            "دقائق اللعب": str(found_player['minutes']),
            "الشباك النظيفة": str(found_player['clean_sheets']),
            "البطاقات الصفراء": str(found_player['yellow_cards']),
            "البطاقات الحمراء": str(found_player['red_cards']),
            "نقاط الفانتسي": str(found_player['total_points'])
        }
        return stats_dict, None

    except Exception as e:
        return None, f"حدث خطأ في الاتصال بقاعدة البيانات: {e}"

# --- واجهة المستخدم (Streamlit UI) ---
st.title("⚽ Premier League Analytics Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 الترتيب", "📅 المباريات", "🏃 إحصائيات اللاعبين"])

# التبويب الأول: جدول الترتيب
with tab1:
    st.subheader("جدول ترتيب الدوري الإنجليزي")
    try:
        df_table = get_table()
        st.dataframe(df_table, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            csv = df_table.to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ تحميل CSV", data=csv, file_name="pl_table.csv", mime="text/csv")
        with col2:
            buffer = BytesIO()
            df_table.to_excel(buffer, index=False)
            st.download_button("⬇️ تحميل Excel", data=buffer.getvalue(), file_name="pl_table.xlsx", mime="application/vnd.ms-excel")
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
            st.warning("لم يتم العثور على مباريات للفريق المطلوب.")
    except Exception as e:
        st.error(f"خطأ في جلب المباريات: {e}")

# التبويب الثالث: إحصائيات اللاعبين
with tab3:
    st.subheader("محرك بحث إحصائيات اللاعبين (قاعدة بيانات FPL الرسمية)")
    player_input = st.text_input("🔍 أدخل اسم اللاعب:", placeholder="مثال: Mohamed Salah, Haaland, Saka...")
    
    if st.button("ابحث عن اللاعب"):
        if player_input:
            with st.spinner("جارِ البحث في قاعدة البيانات..."):
                stats, error = get_player_stats_fpl(player_input)
                if error:
                    st.error(error)
                else:
                    st.success(f"تم العثور على بيانات: {stats.get('الاسم')}")
                    
                    cols = st.columns(3)
                    idx = 0
                    for key, value in stats.items():
                        if key != "الاسم":
                            cols[idx % 3].metric(label=key, value=value)
                            idx += 1
        else:
            st.warning("الرجاء إدخال اسم اللاعب أولاً.")

