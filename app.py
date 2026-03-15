import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from collections import Counter
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="ValueBet Pro Analytics", layout="wide", page_icon="⚽")
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

@st.cache_data(ttl=43200)
def get_fpl_data():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    return requests.get(url, headers=HEADERS).json()

def get_player_stats_fpl(player_name):
    try:
        data = get_fpl_data()
        players = data.get('elements', [])
        teams = {t['id']: t['name'] for t in data.get('teams', [])}
        positions = {p['id']: p['singular_name'] for p in data.get('element_types', [])}
        search_name = player_name.lower().strip()
        for p in players:
            full_name = f"{p['first_name']} {p['second_name']}".lower()
            if search_name in full_name or search_name in p['web_name'].lower():
                return {
                    "الاسم": f"{p['first_name']} {p['second_name']}",
                    "الفريق": teams.get(p['team'], "N/A"),
                    "المركز": positions.get(p['element_type'], "N/A"),
                    "الأهداف": str(p['goals_scored']),
                    "التمريرات": str(p['assists']),
                    "النقاط": str(p['total_points'])
                }, None
        return None, "لاعب غير موجود."
    except: return None, "خطأ في الاتصال."

# --- واجهة المستخدم ---
st.title("⚽ ValueBet Pro: نظام التنبؤ الرياضي")

tabs = st.tabs(["📊 الترتيب", "📅 المباريات", "🏃 اللاعبين", "🧠 غرفة التوقعات", "📈 سجل الدقة"])

with tabs[0]:
    df_table = get_table()
    st.dataframe(df_table, use_container_width=True)

with tabs[1]:
    t_search = st.text_input("🔍 ابحث عن فريق في الجدول القادم:")
    for m in get_fixtures(t_search): st.info(m)

with tabs[2]:
    p_input = st.text_input("🔍 ابحث عن إحصائيات لاعب:")
    if st.button("عرض الإحصائيات"):
        res, err = get_player_stats_fpl(p_input)
        if err: st.error(err)
        else:
            c = st.columns(len(res))
            for i, (k, v) in enumerate(res.items()): c[i].metric(k, v)

with tabs[3]:
    st.subheader("محرك المحاكاة والذكاء الاصطناعي")
    try:
        df = get_table()
        teams = df['الفريق'].tolist()
        df['النقاط'] = pd.to_numeric(df['النقاط'])
        df['فارق الأهداف'] = pd.to_numeric(df['فارق الأهداف'].str.replace('+', ''))
        df['لعب'] = pd.to_numeric(df['لعب'])
        df['القوة'] = (df['النقاط'] + (df['فارق الأهداف'] / 2)) / df['لعب']
        avg_pwr = df['القوة'].mean()

        col_h, col_a = st.columns(2)
        h_team = col_h.selectbox("🏠 صاحب الأرض:", teams, index=0)
        a_team = col_a.selectbox("✈️ الفريق الضيف:", teams, index=1)

        # حساب xG تلقائي
        h_p = df[df['الفريق'] == h_team]['القوة'].values[0]
        a_p = df[df['الفريق'] == a_team]['القوة'].values[0]
        calc_h = 1.3 * (h_p / avg_pwr) * (avg_pwr / a_p) * 1.1
        calc_a = 1.0 * (a_p / avg_pwr) * (avg_pwr / h_p) * 0.9

        st.write("---")
        sc1, sc2 = st.columns(2)
        f_h_xg = sc1.slider(f"تعديل xG {h_team}", 0.0, 5.0, float(round(calc_h, 2)))
        f_a_xg = sc2.slider(f"تعديل xG {a_team}", 0.0, 5.0, float(round(calc_a, 2)))

        if st.button("🚀 تشغيل محاكاة 10,000 مباراة", use_container_width=True):
            sim_h = np.random.poisson(f_h_xg, 10000)
            sim_a = np.random.poisson(f_a_xg, 10000)
            hw, dr, aw = np.sum(sim_h > sim_a), np.sum(sim_h == sim_a), np.sum(sim_h < sim_a)
            common = Counter([f"{h}-{a}" for h, a in zip(sim_h, sim_a)]).most_common(1)[0][0]
            
            st.session_state['last_sim'] = {'h': h_team, 'a': a_team, 'hp': hw/100, 'dp': dr/100, 'ap': aw/100, 'sc': common}
            
            res_c = st.columns(3)
            res_c[0].metric(f"فوز {h_team}", f"{hw/100}%")
            res_c[1].metric("تعادل", f"{dr/100}%")
            res_c[2].metric(f"فوز {a_team}", f"{aw/100}%")
            st.success(f"🎯 النتيجة المتوقعة: {common}")

        if 'last_sim' in st.session_state:
            st.write("---")
            st.markdown("### 🤖 الوكيل القاضي (The Oracle)")
            scout_news = st.text_area("📰 أخبار الكشّاف (إصابات، غيابات، إرهاق):")
            api_key = st.text_input("أدخل مفتاح API (Mistral):", type="password")
            
            if st.button("📝 توليد تقرير القيمة (Value Report)"):
                if api_key:
                    with st.spinner("يتم تحليل البيانات..."):
                        s = st.session_state['last_sim']
                        prompt = f"""أنت محلل ValueBet. مباراة {s['h']} ضد {s['a']}. 
                        الاحتمالات: فوز المضيف {s['hp']}%, تعادل {s['dp']}%, فوز الضيف {s['ap']}%. 
                        النتيجة المتوقعة: {s['sc']}. أخبار إضافية: {scout_news}.
                        اكتب تقريراً من 3 أسطر بالعامية الرياضية حول 'القيمة' في هذه المباراة."""
                        try:
                            r = requests.post("https://api.mistral.ai/v1/chat/completions",
                                            headers={"Authorization": f"Bearer {api_key}"},
                                            json={"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}]})
                            st.info(r.json()['choices'][0]['message']['content'])
                        except: st.error("فشل الاتصال بالذكاء الاصطناعي.")
            
            if st.button("💾 حفظ التوقع في السجل"):
                s = st.session_state['last_sim']
                row = pd.DataFrame([{"التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d"), "المباراة": f"{s['h']} v {s['a']}", "التوقع": s['sc'], "الاحتمال": f"{max(s['hp'], s['ap'])}%"}])
                row.to_csv("history.csv", mode='a', header=not os.path.exists("history.csv"), index=False)
                st.toast("تم الحفظ!")

    except Exception as e: st.error(f"خطأ في المحرك: {e}")

with tabs[4]:
    st.subheader("سجل التوقعات السابقة")
    if os.path.exists("history.csv"):
        st.table(pd.read_csv("history.csv"))
        if st.button("🗑️ مسح السجل"): 
            os.remove("history.csv")
            st.rerun()
    else: st.info("السجل فارغ حالياً.")

