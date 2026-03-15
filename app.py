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
    data = []
    rows = soup.find_all("li", class_=re.compile(r"standings__row", re.I))
    for row in rows:
        team = row.find(["p", "span", "div"], class_=re.compile(r"standings__teamName", re.I))
        stats = row.find_all("div", class_=re.compile(r"standings__cell", re.I))
        if team and len(stats) >= 8:
            data.append({
                "المركز": stats[0].text.strip(),
                "الفريق": team.text.strip(),
                "لعب": stats[2].text.strip(),
                "فاز": stats[3].text.strip(),
                "تعادل": stats[4].text.strip(),
                "خسر": stats[5].text.strip(),
                "فارق الأهداف": stats[6].text.strip(),
                "النقاط": stats[7].text.strip()
            })
    return pd.DataFrame(data)

def get_team_news(team_name):
    try:
        search_url = f"https://www.google.com/search?q={team_name}+fc+latest+news+injuries&tbm=nws"
        response = requests.get(search_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "lxml")
        headlines = [t.get_text() for t in soup.find_all('div', role='heading')[:3]]
        return " | ".join(headlines) if headlines else "لا توجد أخبار حديثة متاحة."
    except: return "فشل جلب الأخبار الحية."

@st.cache_data(ttl=3600)
def get_fixtures(team_filter=""):
    link = "https://onefootball.com/en/competition/premier-league-9/fixtures"
    source = requests.get(link, headers=HEADERS).text
    page = BeautifulSoup(source, "lxml")
    fix_elements = page.find_all("a", class_=re.compile(r"matchCard", re.I))
    fixtures = [match.get_text(separator=" | ").strip() for match in fix_elements]
    if team_filter: fixtures = [f for f in fixtures if team_filter.lower() in f.lower()]
    return fixtures

# --- واجهة المستخدم ---
st.title("⚽ ValueBet Pro: المحلل الذكي")

tab_list = ["📊 الترتيب", "📅 المباريات", "🧠 غرفة التوقعات", "📈 سجل الدقة"]
tabs = st.tabs(tab_list)

with tabs[0]:
    df_table = get_table()
    st.dataframe(df_table, use_container_width=True)

with tabs[1]:
    t_search = st.text_input("🔍 ابحث عن فريق في المباريات:")
    for m in get_fixtures(t_search): st.info(m)

with tabs[2]:
    st.subheader("محرك المحاكاة والذكاء الاصطناعي")
    try:
        df = get_table()
        teams = df['الفريق'].tolist()
        df['النقاط'] = pd.to_numeric(df['النقاط'])
        df['فارق الأهداف'] = pd.to_numeric(df['فارق الأهداف'].str.replace('+', ''))
        df['لعب'] = pd.to_numeric(df['لعب'])
        df['القوة'] = (df['النقاط'] + (df['فارق الأهداف'] / 2)) / df['لعب']
        avg_pwr = df['القوة'].mean()

        c1, c2 = st.columns(2)
        h_team = c1.selectbox("🏠 المضيف:", teams, index=0)
        a_team = c2.selectbox("✈️ الضيف:", teams, index=1)

        h_p, a_p = df[df['الفريق'] == h_team]['القوة'].values[0], df[df['الفريق'] == a_team]['القوة'].values[0]
        calc_h = 1.3 * (h_p / avg_pwr) * (avg_pwr / a_p) * 1.1
        calc_a = 1.0 * (a_p / avg_pwr) * (avg_pwr / h_p) * 0.9

        st.write("---")
        sc1, sc2 = st.columns(2)
        f_h_xg = sc1.slider(f"تعديل xG {h_team}", 0.0, 5.0, float(round(calc_h, 2)))
        f_a_xg = sc2.slider(f"تعديل xG {a_team}", 0.0, 5.0, float(round(calc_a, 2)))

        if st.button("🚀 تشغيل محاكاة 10,000 مباراة", use_container_width=True):
            sim_h, sim_a = np.random.poisson(f_h_xg, 10000), np.random.poisson(f_a_xg, 10000)
            hw, dr, aw = np.sum(sim_h > sim_a), np.sum(sim_h == sim_a), np.sum(sim_h < sim_a)
            common = Counter([f"{h}-{a}" for h, a in zip(sim_h, sim_a)]).most_common(1)[0][0]
            st.session_state['last_sim'] = {'h': h_team, 'a': a_team, 'hp': hw/100, 'dp': dr/100, 'ap': aw/100, 'sc': common}
            
            res_c = st.columns(3)
            res_c[0].metric(f"فوز {h_team}", f"{hw/100}%")
            res_c[1].metric("تعادل", f"{dr/100}%")
            res_c[2].metric(f"فوز {a_team}", f"{aw/100}%")
            st.success(f"🎯 النتيجة الأكثر توقعاً: {common}")

        if 'last_sim' in st.session_state:
            st.write("---")
            st.markdown("### 🤖 الوكيل القاضي (The Oracle)")
            
            if st.button("🔍 جلب أخبار الفريقين"):
                with st.spinner("جاري مسح الأخبار..."):
                    st.session_state['current_news'] = f"أخبار {h_team}: {get_team_news(h_team)}\nأخبار {a_team}: {get_team_news(a_team)}"
            
            scout_news = st.text_area("📰 مدخلات الكشّاف:", value=st.session_state.get('current_news', ""), height=100)
            
            # جلب المفتاح من Secrets أو المستخدم
            api_key = st.secrets.get("MISTRAL_API_KEY", st.text_input("أدخل مفتاح Mistral API:", type="password"))
            
            if st.button("📝 تحليل القيمة (Value Report)"):
                if api_key:
                    with st.spinner("الذكاء الاصطناعي يحلل الآن..."):
                        s = st.session_state['last_sim']
                        prompt = f"حلل مباراة {s['h']} ضد {s['a']}. الأرقام: فوز المضيف {s['hp']}%, تعادل {s['dp']}%, فوز الضيف {s['ap']}%. الأخبار: {scout_news}. هل هناك قيمة مراهنة؟ أجب بذكاء واختصار بالعامية."
                        try:
                            r = requests.post("https://api.mistral.ai/v1/chat/completions",
                                            headers={"Authorization": f"Bearer {api_key}"},
                                            json={"model": "mistral-small-latest", "messages": [{"role": "user", "content": prompt}]})
                            st.info(r.json()['choices'][0]['message']['content'])
                        except: st.error("خطأ في الاتصال.")
            
            if st.button("💾 حفظ في السجل"):
                s = st.session_state['last_sim']
                row = pd.DataFrame([{"التاريخ": pd.Timestamp.now().strftime("%Y-%m-%d"), "المباراة": f"{s['h']} v {s['a']}", "التوقع": s['sc'], "الاحتمال": f"{max(s['hp'], s['ap'])}%"}])
                row.to_csv("history.csv", mode='a', header=not os.path.exists("history.csv"), index=False)
                st.toast("تم الحفظ!")

    except Exception as e: st.error(f"خطأ: {e}")

with tabs[3]:
    if os.path.exists("history.csv"):
        st.table(pd.read_csv("history.csv"))
        if st.button("🗑️ مسح"): os.remove("history.csv"); st.rerun()
    else: st.info("السجل فارغ.")
