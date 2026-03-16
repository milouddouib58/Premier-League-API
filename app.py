import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from collections import Counter
import os
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import poisson

# ============================================================
# ⚙️ إعدادات الصفحة
# ============================================================
st.set_page_config(
    page_title="ValueBet Pro Analytics",
    layout="wide",
    page_icon="⚽",
    initial_sidebar_state="expanded"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
}

# ============================================================
# 🎨 التصميم المخصص
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700;900&display=swap');
    * {
        font-family: 'Tajawal', sans-serif;
    }
    .main {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 50%, #0d0d2b 100%);
    }
    /* Header Glow */
    .main-header {
        text-align: center;
        padding: 30px;
        background: linear-gradient(135deg, #00d4ff22, #7b2ff744, #ff006622);
        border-radius: 20px;
        border: 1px solid #7b2ff755;
        margin-bottom: 30px;
        animation: headerPulse 3s ease-in-out infinite;
    }
    @keyframes headerPulse {
        0%, 100% { box-shadow: 0 0 30px #7b2ff733; }
        50% { box-shadow: 0 0 60px #7b2ff766, 0 0 100px #00d4ff22; }
    }
    .main-header h1 {
        font-size: 2.8em;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7, #ff0066);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-header p {
        color: #8888aa;
        font-size: 1.1em;
        margin-top: 5px;
    }
    /* Cards */
    .glass-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(123,47,247,0.3);
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        backdrop-filter: blur(20px);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: #00d4ff;
        box-shadow: 0 8px 40px rgba(0,212,255,0.15);
        transform: translateY(-2px);
    }
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(0,212,255,0.1), rgba(123,47,247,0.1));
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0,212,255,0.3);
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        color: #8888aa;
        font-size: 0.9em;
        margin-top: 5px;
    }
    /* Win Probability */
    .prob-home {
        background: linear-gradient(135deg, rgba(0,200,83,0.15), rgba(0,200,83,0.05));
        border: 1px solid rgba(0,200,83,0.4);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    }
    .prob-draw {
        background: linear-gradient(135deg, rgba(255,193,7,0.15), rgba(255,193,7,0.05));
        border: 1px solid rgba(255,193,7,0.4);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    }
    .prob-away {
        background: linear-gradient(135deg, rgba(244,67,54,0.15), rgba(244,67,54,0.05));
        border: 1px solid rgba(244,67,54,0.4);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
    }
    .prob-value {
        font-size: 3em;
        font-weight: 900;
    }
    /* ValueBet Alert */
    .valuebet-alert {
        background: linear-gradient(135deg, rgba(0,255,136,0.1), rgba(0,200,83,0.05));
        border: 2px solid #00ff88;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        animation: valuePulse 2s ease-in-out infinite;
    }
    @keyframes valuePulse {
        0%, 100% { box-shadow: 0 0 20px rgba(0,255,136,0.2); }
        50% { box-shadow: 0 0 40px rgba(0,255,136,0.4); }
    }
    /* Agent Cards */
    .agent-card {
        border-radius: 16px;
        padding: 20px;
        margin: 10px 0;
    }
    .agent-scout {
        background: linear-gradient(135deg, rgba(33,150,243,0.1), transparent);
        border: 1px solid rgba(33,150,243,0.4);
    }
    .agent-tactician {
        background: linear-gradient(135deg, rgba(156,39,176,0.1), transparent);
        border: 1px solid rgba(156,39,176,0.4);
    }
    .agent-judge {
        background: linear-gradient(135deg, rgba(255,152,0,0.1), transparent);
        border: 1px solid rgba(255,152,0,0.4);
    }
    /* Table Styling */
    .dataframe {
        border-radius: 12px !important;
        overflow: hidden;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 12px 24px;
        color: #8888aa;
        font-weight: 700;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7b2ff7, #00d4ff) !important;
        color: white !important;
    }
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d2b, #1a1a3e) !important;
        border-right: 1px solid #7b2ff733;
    }
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7b2ff7, #00d4ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 8px 30px rgba(123,47,247,0.4) !important;
    }
    /* Score Display */
    .score-display {
        font-size: 4em;
        font-weight: 900;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #00d4ff, #7b2ff7, #ff0066);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: scoreGlow 2s ease-in-out infinite;
    }
    @keyframes scoreGlow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.3); }
    }
    /* Fixture Card */
    .fixture-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(123,47,247,0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.3s ease;
    }
    .fixture-card:hover {
        border-color: #00d4ff;
        background: rgba(0,212,255,0.05);
    }
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0a1a;
    }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(#7b2ff7, #00d4ff);
        border-radius: 10px;
    }
    .accuracy-good {
        color: #00ff88;
    }
    .accuracy-mid {
        color: #ffc107;
    }
    .accuracy-bad {
        color: #ff4444;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 📡 دوال جلب البيانات
# ============================================================
@st.cache_data(ttl=3600)
def get_table():
    """جلب جدول ترتيب الدوري الإنجليزي"""
    link = "https://onefootball.com/en/competition/premier-league-9/table"
    try:
        source = requests.get(link, headers=HEADERS, timeout=10).text
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
                    "فارق": stats[6].text.strip(),
                    "النقاط": stats[7].text.strip()
                })
        if data:
            return pd.DataFrame(data)
        else:
            return get_fallback_table()
    except:
        return get_fallback_table()

def get_fallback_table():
    """بيانات احتياطية في حالة فشل الجلب"""
    teams_data = [
        {"المركز": "1", "الفريق": "Liverpool", "لعب": "33", "فاز": "25", "تعادل": "6", "خسر": "2", "فارق": "+45", "النقاط": "81"},
        {"المركز": "2", "الفريق": "Arsenal", "لعب": "33", "فاز": "22", "تعادل": "7", "خسر": "4", "فارق": "+40", "النقاط": "73"},
        {"المركز": "3", "الفريق": "Nottingham Forest", "لعب": "33", "فاز": "20", "تعادل": "7", "خسر": "6", "فارق": "+15", "النقاط": "67"},
        {"المركز": "4", "الفريق": "Chelsea", "لعب": "33", "فاز": "18", "تعادل": "8", "خسر": "7", "فارق": "+18", "النقاط": "62"},
        {"المركز": "5", "الفريق": "Aston Villa", "لعب": "33", "فاز": "17", "تعادل": "8", "خسر": "8", "فارق": "+12", "النقاط": "59"},
        {"المركز": "6", "الفريق": "Brighton", "لعب": "33", "فاز": "16", "تعادل": "9", "خسر": "8", "فارق": "+10", "النقاط": "57"},
        {"المركز": "7", "الفريق": "Newcastle", "لعب": "33", "فاز": "16", "تعادل": "8", "خسر": "9", "فارق": "+14", "النقاط": "56"},
        {"المركز": "8", "الفريق": "Manchester City", "لعب": "33", "فاز": "16", "تعادل": "6", "خسر": "11", "فارق": "+16", "النقاط": "54"},
        {"المركز": "9", "الفريق": "Bournemouth", "لعب": "33", "فاز": "15", "تعادل": "7", "خسر": "11", "فارق": "+5", "النقاط": "52"},
        {"المركز": "10", "الفريق": "Fulham", "لعب": "33", "فاز": "14", "تعادل": "8", "خسر": "11", "فارق": "+2", "النقاط": "50"},
        {"المركز": "11", "الفريق": "Manchester United", "لعب": "33", "فاز": "13", "تعادل": "5", "خسر": "15", "فارق": "-8", "النقاط": "44"},
        {"المركز": "12", "الفريق": "Brentford", "لعب": "33", "فاز": "12", "تعادل": "7", "خسر": "14", "فارق": "-4", "النقاط": "43"},
        {"المركز": "13", "الفريق": "Tottenham", "لعب": "33", "فاز": "12", "تعادل": "4", "خسر": "17", "فارق": "-3", "النقاط": "40"},
        {"المركز": "14", "الفريق": "West Ham", "لعب": "33", "فاز": "11", "تعادل": "6", "خسر": "16", "فارق": "-14", "النقاط": "39"},
        {"المركز": "15", "الفريق": "Crystal Palace", "لعب": "33", "فاز": "9", "تعادل": "10", "خسر": "14", "فارق": "-8", "النقاط": "37"},
        {"المركز": "16", "الفريق": "Everton", "لعب": "33", "فاز": "9", "تعادل": "9", "خسر": "15", "فارق": "-12", "النقاط": "36"},
        {"المركز": "17", "الفريق": "Wolverhampton", "لعب": "33", "فاز": "9", "تعادل": "7", "خسر": "17", "فارق": "-20", "النقاط": "34"},
        {"المركز": "18", "الفريق": "Ipswich Town", "لعب": "33", "فاز": "5", "تعادل": "12", "خسر": "16", "فارق": "-22", "النقاط": "27"},
        {"المركز": "19", "الفريق": "Leicester City", "لعب": "33", "فاز": "5", "تعادل": "8", "خسر": "20", "فارق": "-34", "النقاط": "23"},
        {"المركز": "20", "الفريق": "Southampton", "لعب": "33", "فاز": "3", "تعادل": "6", "خسر": "24", "فارق": "-42", "النقاط": "15"},
    ]
    return pd.DataFrame(teams_data)

@st.cache_data(ttl=3600)
def get_fixtures(team_filter=""):
    """جلب المباريات القادمة"""
    link = "https://onefootball.com/en/competition/premier-league-9/fixtures"
    try:
        source = requests.get(link, headers=HEADERS, timeout=10).text
        page = BeautifulSoup(source, "lxml")
        match_pattern = re.compile(r"matchCard", re.IGNORECASE)
        fix_elements = page.find_all("a", class_=match_pattern)
        fixtures = [match.get_text(separator=" | ").strip() for match in fix_elements]
        if team_filter:
            fixtures = [f for f in fixtures if team_filter.lower() in f.lower()]
        return fixtures
    except:
        return ["تعذر جلب المباريات - تحقق من الاتصال"]

@st.cache_data(ttl=43200)
def get_fpl_data():
    """جلب بيانات Fantasy Premier League"""
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    return requests.get(url, headers=HEADERS, timeout=10).json()

def get_player_stats_fpl(player_name):
    """البحث عن إحصائيات لاعب من FPL"""
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
                    "الدقائق": str(p['minutes']),
                    "النقاط FPL": str(p['total_points']),
                    "الأهداف المتوقعة xG": str(p.get('expected_goals', 'N/A')),
                    "التمريرات المتوقعة xA": str(p.get('expected_assists', 'N/A')),
                    "الأهداف المتوقعة ضد xGC": str(p.get('expected_goals_conceded', 'N/A')),
                }, None
        return None, "❌ لاعب غير موجود في قاعدة البيانات."
    except Exception as e:
        return None, f"⚠️ خطأ في الاتصال: {e}"

# ============================================================
# 🧮 المرحلة الأولى: محرك المحاكاة (Monte Carlo + Poisson)
# ============================================================
class PoissonEngine:
    """محرك بواسون للقوة الهجومية والدفاعية"""
    def __init__(self, df):
        self.df = df.copy()
        self._prepare_data()

    def _prepare_data(self):
        """تحضير البيانات وحساب القوة"""
        self.df['النقاط_رقم'] = pd.to_numeric(self.df['النقاط'], errors='coerce')
        self.df['لعب_رقم'] = pd.to_numeric(self.df['لعب'], errors='coerce')
        self.df['فاز_رقم'] = pd.to_numeric(self.df['فاز'], errors='coerce')
        self.df['خسر_رقم'] = pd.to_numeric(self.df['خسر'], errors='coerce')
        self.df['تعادل_رقم'] = pd.to_numeric(self.df['تعادل'], errors='coerce')
        # فارق الأهداف
        self.df['فارق_رقم'] = self.df['فارق'].apply(
            lambda x: int(str(x).replace('+', '')) if pd.notna(x) else 0
        )
        # تقدير الأهداف المسجلة والمستقبلة
        # الأهداف المسجلة ≈ (فاز * 2.2 + تعادل * 1.1 + خسر * 0.6) تقريبياً
        # أو نستخدم الفارق + تقدير
        total_matches = self.df['لعب_رقم'].sum() / 2
        league_avg = 1.35  # متوسط أهداف الفريق الواحد في البريميرليج
        # حساب معدل النقاط لكل مباراة كمؤشر للقوة
        self.df['معدل_النقاط'] = self.df['النقاط_رقم'] / self.df['لعب_رقم']
        # القوة الهجومية (Attack Strength)
        max_pts_rate = self.df['معدل_النقاط'].max()
        min_pts_rate = self.df['معدل_النقاط'].min()
        self.df['قوة_هجومية'] = (
            0.7 + 0.9 * (self.df['معدل_النقاط'] - min_pts_rate) / (max_pts_rate - min_pts_rate + 0.01)
        )
        # القوة الدفاعية (Defense Strength) - أقل = أفضل
        self.df['قوة_دفاعية'] = (
            0.7 + 0.9 * (1 - (self.df['معدل_النقاط'] - min_pts_rate) / (max_pts_rate - min_pts_rate + 0.01))
        )
        # تعديل بناءً على فارق الأهداف
        gd_factor = self.df['فارق_رقم'] / (self.df['لعب_رقم'] * 2 + 1)
        self.df['قوة_هجومية'] += gd_factor * 0.3
        self.df['قوة_دفاعية'] -= gd_factor * 0.3
        # ضمان قيم موجبة
        self.df['قوة_هجومية'] = self.df['قوة_هجومية'].clip(lower=0.3)
        self.df['قوة_دفاعية'] = self.df['قوة_دفاعية'].clip(lower=0.3)

    def get_team_strength(self, team_name):
        """الحصول على قوة فريق معين"""
        team_row = self.df[self.df['الفريق'] == team_name]
        if team_row.empty:
            return {'attack': 1.0, 'defense': 1.0, 'pts_rate': 1.5}
        return {
            'attack': team_row['قوة_هجومية'].values[0],
            'defense': team_row['قوة_دفاعية'].values[0],
            'pts_rate': team_row['معدل_النقاط'].values[0]
        }

    def calculate_xg(self, home_team, away_team, home_adv=1.15):
        """حساب الأهداف المتوقعة لكل فريق"""
        home = self.get_team_strength(home_team)
        away = self.get_team_strength(away_team)
        league_avg = 1.35
        # xG المضيف = متوسط الدوري × قوة هجوم المضيف × ضعف دفاع الضيف × ميزة الأرض
        home_xg = league_avg * home['attack'] * away['defense'] * home_adv
        # xG الضيف = متوسط الدوري × قوة هجوم الضيف × ضعف دفاع المضيف
        away_xg = league_avg * away['attack'] * home['defense'] * (2 - home_adv)
        return round(home_xg, 2), round(away_xg, 2)

    def poisson_probability(self, xg, goals):
        """احتمال تسجيل عدد محدد من الأهداف"""
        return poisson.pmf(goals, xg)

    def match_probability_matrix(self, home_xg, away_xg, max_goals=7):
        """مصفوفة احتمالات النتائج"""
        matrix = np.zeros((max_goals, max_goals))
        for h in range(max_goals):
            for a in range(max_goals):
                matrix[h][a] = self.poisson_probability(home_xg, h) * \
                    self.poisson_probability(away_xg, a)
        return matrix

    def match_outcome_probs(self, home_xg, away_xg):
        """حساب احتمالات النتيجة (فوز/تعادل/خسارة)"""
        matrix = self.match_probability_matrix(home_xg, away_xg)
        max_g = matrix.shape[0]
        home_win = sum(matrix[h][a] for h in range(max_g) for a in range(max_g) if h > a)
        draw = sum(matrix[h][a] for h in range(max_g) for a in range(max_g) if h == a)
        away_win = sum(matrix[h][a] for h in range(max_g) for a in range(max_g) if h < a)
        total = home_win + draw + away_win
        return {
            'home_win': round(home_win / total * 100, 1),
            'draw': round(draw / total * 100, 1),
            'away_win': round(away_win / total * 100, 1)
        }

class MonteCarloSimulator:
    """محرك محاكاة مونت كارلو"""
    def __init__(self, n_simulations=10000):
        self.n_sims = n_simulations

    def simulate_match(self, home_xg, away_xg):
        """محاكاة المباراة n مرة"""
        home_goals = np.random.poisson(home_xg, self.n_sims)
        away_goals = np.random.poisson(away_xg, self.n_sims)
        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)
        # النتائج الأكثر شيوعاً
        scores = [f"{h}-{a}" for h, a in zip(home_goals, away_goals)]
        score_counts = Counter(scores).most_common(10)
        # إحصائيات إضافية
        avg_home = np.mean(home_goals)
        avg_away = np.mean(away_goals)
        avg_total = avg_home + avg_away
        # احتمال أكثر/أقل من 2.5
        over_25 = np.sum((home_goals + away_goals) > 2.5) / self.n_sims * 100
        under_25 = 100 - over_25
        # احتمال كلا الفريقين يسجل
        btts_yes = np.sum((home_goals > 0) & (away_goals > 0)) / self.n_sims * 100
        btts_no = 100 - btts_yes
        return {
            'home_win_pct': round(home_wins / self.n_sims * 100, 1),
            'draw_pct': round(draws / self.n_sims * 100, 1),
            'away_win_pct': round(away_wins / self.n_sims * 100, 1),
            'most_likely_scores': score_counts,
            'avg_home_goals': round(avg_home, 2),
            'avg_away_goals': round(avg_away, 2),
            'avg_total_goals': round(avg_total, 2),
            'over_25_pct': round(over_25, 1),
            'under_25_pct': round(under_25, 1),
            'btts_yes_pct': round(btts_yes, 1),
            'btts_no_pct': round(btts_no, 1),
            'home_goals_dist': home_goals,
            'away_goals_dist': away_goals
        }

# ============================================================
# 🎯 المرحلة الثانية: قناص القيمة (ValueBet Finder)
# ============================================================
class ValueBetFinder:
    """كاشف رهانات القيمة"""
    @staticmethod
    def find_value(model_prob, market_prob, min_edge=5.0):
        """
        البحث عن القيمة
        model_prob: احتمال النموذج (%)
        market_prob: احتمال السوق (%)
        min_edge: الحد الأدنى للميزة (%)
        """
        edge = model_prob - market_prob
        value_rating = edge / market_prob * 100 if market_prob > 0 else 0
        return {
            'edge': round(edge, 1),
            'value_rating': round(value_rating, 1),
            'is_value': edge >= min_edge,
            'kelly_fraction': ValueBetFinder.kelly_criterion(model_prob, market_prob)
        }

    @staticmethod
    def kelly_criterion(model_prob, market_prob):
        """حساب نسبة كيلي المثلى"""
        if market_prob <= 0 or model_prob <= 0:
            return 0
        p = model_prob / 100
        decimal_odds = 100 / market_prob
        q = 1 - p
        b = decimal_odds - 1
        if b <= 0:
            return 0
        kelly = (b * p - q) / b
        # نستخدم ربع كيلي للأمان
        return max(0, round(kelly * 25, 1))

    @staticmethod
    def implied_probability(decimal_odds):
        """تحويل الأرجحية إلى احتمال ضمني"""
        if decimal_odds <= 0:
            return 0
        return round(100 / decimal_odds, 1)

# ============================================================
# 🤖 المرحلة الثالثة: نظام الوكلاء (Multi-Agent AI)
# ============================================================
class AgentSystem:
    """نظام الوكلاء المتعددين"""
    def __init__(self, api_key, provider="mistral"):
        self.api_key = api_key
        self.provider = provider

    def _call_ai(self, prompt, system_prompt=""):
        """استدعاء نموذج الذكاء الاصطناعي"""
        try:
            if self.provider == "mistral":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                r = requests.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-small-latest",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                return r.json()['choices'][0]['message']['content']
            elif self.provider == "cerebras":
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})
                r = requests.post(
                    "https://api.cerebras.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-4-scout-17b-16e-instruct",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30
                )
                return r.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"⚠️ خطأ: {str(e)}"

    def scout_agent(self, home_team, away_team, sim_results, scout_news=""):
        """وكيل الكشّاف - تحليل البيانات الخام"""
        prompt = f"""📊 تقرير البيانات الخام:
المباراة: {home_team} (مضيف) ضد {away_team} (ضيف)
نتائج محاكاة 10,000 مباراة:
- فوز {home_team}: {sim_results['home_win_pct']}%
- تعادل: {sim_results['draw_pct']}%
- فوز {away_team}: {sim_results['away_win_pct']}%
متوسط الأهداف المتوقعة:
- {home_team}: {sim_results['avg_home_goals']} هدف
- {away_team}: {sim_results['avg_away_goals']} هدف
- المجموع: {sim_results['avg_total_goals']} هدف
أكثر/أقل 2.5: {sim_results['over_25_pct']}% / {sim_results['under_25_pct']}%
كلا الفريقين يسجل: {sim_results['btts_yes_pct']}%
النتائج الأكثر احتمالاً:
{chr(10).join([f"   {s}: {c/100:.1f}%" for s, c in sim_results['most_likely_scores'][:5]])}
أخبار إضافية: {scout_news if scout_news else 'لا توجد أخبار'}
حلل هذه البيانات كخبير إحصائي رياضي. ركز على الأرقام والاتجاهات.
اكتب تقريرك في 4-5 أسطر بالعربية."""
        system = "أنت وكيل كشّاف رياضي متخصص في تحليل البيانات الإحصائية لمباريات كرة القدم. تقدم تحليلات دقيقة مبنية على الأرقام."
        return self._call_ai(prompt, system)

    def tactician_agent(self, home_team, away_team, sim_results, scout_report):
        """وكيل التكتيكي - التحليل التكتيكي"""
        prompt = f"""🎯 التحليل التكتيكي المطلوب:
المباراة: {home_team} ضد {away_team}
تقرير الكشّاف:
{scout_report}
البيانات الرئيسية:
- احتمال فوز المضيف: {sim_results['home_win_pct']}%
- احتمال التعادل: {sim_results['draw_pct']}%
- احتمال فوز الضيف: {sim_results['away_win_pct']}%
- متوسط الأهداف: {sim_results['avg_total_goals']}
بناءً على تقرير الكشّاف والبيانات، قدم تحليلك التكتيكي:
1. ما هو السيناريو الأرجح للمباراة؟
2. ما هي نقاط القوة والضعف لكل فريق؟
3. ما هو توقعك النهائي؟
اكتب تقريرك في 4-5 أسطر بالعربية بأسلوب المحلل الرياضي."""
        system = "أنت محلل تكتيكي لكرة القدم. تقدم رؤى تكتيكية عميقة بأسلوب احترافي."
        return self._call_ai(prompt, system)

    def judge_agent(self, home_team, away_team, sim_results, scout_report, tactician_report, value_data=None):
        """وكيل القاضي - الحكم النهائي"""
        value_section = ""
        if value_data:
            value_section = f"""
تحليل القيمة:
- ميزة فوز المضيف: {value_data.get('home_edge', 'N/A')}%
- ميزة التعادل: {value_data.get('draw_edge', 'N/A')}%
- ميزة فوز الضيف: {value_data.get('away_edge', 'N/A')}%
"""
        prompt = f"""⚖️ القرار النهائي مطلوب:
المباراة: {home_team} ضد {away_team}
📊 تقرير الكشّاف:
{scout_report}
🎯 تقرير التكتيكي:
{tactician_report}
📈 بيانات المحاكاة:
- فوز {home_team}: {sim_results['home_win_pct']}%
- تعادل: {sim_results['draw_pct']}%
- فوز {away_team}: {sim_results['away_win_pct']}%
- النتيجة الأكثر احتمالاً: {sim_results['most_likely_scores'][0][0]}
{value_section}
بصفتك القاضي النهائي، اكتب:
1. ✅ التوقع النهائي (نتيجة محددة)
2. 📊 مستوى الثقة (%)
3. 💡 أفضل فرصة قيمة في هذه المباراة
4. ⚠️ المخاطر المحتملة
اكتب تقريرك النهائي في 5-6 أسطر بالعربية كحكم رياضي محترف."""
        system = "أنت القاضي النهائي في نظام تحليل كرة القدم. تجمع بين تقارير الكشّاف والتكتيكي لإصدار حكمك النهائي بحكمة ودقة."
        return self._call_ai(prompt, system)

# ============================================================
# 📊 دوال الرسوم البيانية
# ============================================================
def create_probability_chart(home_team, away_team, sim_results):
    """رسم بياني لاحتمالات النتيجة"""
    fig = go.Figure()
    categories = [f'فوز {home_team}', 'تعادل', f'فوز {away_team}']
    values = [sim_results['home_win_pct'], sim_results['draw_pct'], sim_results['away_win_pct']]
    colors = ['#00c853', '#ffc107', '#ff4444']
    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker_color=colors,
        text=[f'{v}%' for v in values],
        textposition='auto',
        textfont=dict(size=18, color='white', family='Tajawal')
    ))
    fig.update_layout(
        title=dict(text='احتمالات نتيجة المباراة', font=dict(size=20, color='white', family='Tajawal')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title='النسبة المئوية %', color='#8888aa', gridcolor='rgba(255,255,255,0.05)'),
        xaxis=dict(color='white'),
        font=dict(family='Tajawal', color='white'),
        height=400
    )
    return fig

def create_goals_distribution(home_team, away_team, sim_results):
    """رسم بياني لتوزيع الأهداف"""
    fig = go.Figure()
    home_counts = np.bincount(sim_results['home_goals_dist'], minlength=8)[:8]
    away_counts = np.bincount(sim_results['away_goals_dist'], minlength=8)[:8]
    goals = list(range(8))
    fig.add_trace(go.Bar(
        name=home_team,
        x=goals,
        y=home_counts / len(sim_results['home_goals_dist']) * 100,
        marker_color='#00d4ff',
        opacity=0.7
    ))
    fig.add_trace(go.Bar(
        name=away_team,
        x=goals,
        y=away_counts / len(sim_results['away_goals_dist']) * 100,
        marker_color='#ff0066',
        opacity=0.7
    ))
    fig.update_layout(
        title=dict(text='توزيع الأهداف المتوقعة', font=dict(size=20, color='white', family='Tajawal')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(title='عدد الأهداف', color='#8888aa', dtick=1),
        yaxis=dict(title='الاحتمال %', color='#8888aa', gridcolor='rgba(255,255,255,0.05)'),
        barmode='group',
        font=dict(family='Tajawal', color='white'),
        legend=dict(font=dict(color='white')),
        height=400
    )
    return fig

def create_score_heatmap(home_team, away_team, home_xg, away_xg):
    """خريطة حرارية لاحتمالات النتائج"""
    max_goals = 6
    matrix = np.zeros((max_goals, max_goals))
    for h in range(max_goals):
        for a in range(max_goals):
            matrix[h][a] = poisson.pmf(h, home_xg) * poisson.pmf(a, away_xg) * 100
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[str(i) for i in range(max_goals)],
        y=[str(i) for i in range(max_goals)],
        text=np.round(matrix, 1),
        texttemplate='%{text}%',
        colorscale='Viridis',
        hovertemplate=f'{home_team}: %{{y}} - {away_team}: %{{x}}<br>الاحتمال: %{{z:.1f}}%'
    ))
    fig.update_layout(
        title=dict(text='خريطة حرارية لاحتمالات النتائج', font=dict(size=20, color='white', family='Tajawal')),
        xaxis=dict(title=f'أهداف {away_team}', color='#8888aa'),
        yaxis=dict(title=f'أهداف {home_team}', color='#8888aa'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Tajawal', color='white'),
        height=450
    )
    return fig

# ============================================================
# 🖥️ واجهة المستخدم الرئيسية
# ============================================================
# Header
st.markdown("""
<div class="main-header">
    <h1>⚽ ValueBet Pro Analytics</h1>
    <p>نظام التنبؤ الرياضي المتقدم | محاكاة مونت كارلو + ذكاء اصطناعي متعدد الوكلاء</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ إعدادات النظام")
    st.markdown("---")
    n_sims = st.select_slider(
        "🎲 عدد المحاكاات",
        options=[1000, 5000, 10000, 50000, 100000],
        value=10000,
        help="كلما زاد العدد، زادت الدقة لكن بطأ المعالجة"
    )
    home_advantage = st.slider(
        "🏠 عامل ميزة الأرض",
        min_value=1.0,
        max_value=1.4,
        value=1.15,
        step=0.05,
        help="1.0 = لا ميزة، 1.4 = ميزة كبيرة"
    )
    st.markdown("---")
    st.markdown("### 🤖 إعدادات AI")
    ai_provider = st.selectbox("مزود الذكاء الاصطناعي:", ["mistral", "cerebras"])
    api_key = st.text_input("🔑 مفتاح API:", type="password")
    st.markdown("---")
    st.markdown("### 🎯 إعدادات القيمة")
    min_edge = st.slider(
        "الحد الأدنى للميزة %",
        min_value=1.0,
        max_value=20.0,
        value=5.0,
        step=0.5
    )
    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; color:#666; font-size:0.8em;'>
        <p>ValueBet Pro v3.0</p>
        <p>صنع بـ ❤️ بواسطة محمد الأمين</p>
    </div>
    """, unsafe_allow_html=True)

# Tabs
tabs = st.tabs([
    "📊 الترتيب",
    "📅 المباريات",
    "🏃 اللاعبين",
    "🧠 غرفة التوقعات",
    "🎯 قناص القيمة",
    "🤖 الوكلاء AI",
    "📈 سجل الدقة"
])

# ============================================================
# TAB 0: الترتيب
# ============================================================
with tabs[0]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📊 جدول ترتيب الدوري الإنجليزي الممتاز")
    df_table = get_table()
    if not df_table.empty:
        # تلوين الجدول
        def highlight_table(row):
            pos = int(row['المركز']) if str(row['المركز']).isdigit() else 0
            if pos <= 4:
                return ['background-color: rgba(0,200,83,0.15)'] * len(row)
            elif pos <= 6:
                return ['background-color: rgba(33,150,243,0.15)'] * len(row)
            elif pos >= 18:
                return ['background-color: rgba(244,67,54,0.15)'] * len(row)
            return [''] * len(row)
        styled_df = df_table.style.apply(highlight_table, axis=1)
        st.dataframe(styled_df, use_container_width=True, height=750)
        # إحصائيات سريعة
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">🏆</div>
                <div class="metric-label">المتصدر: {df_table.iloc[0]['الفريق']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            top_pts = df_table.iloc[0]['النقاط']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{top_pts}</div>
                <div class="metric-label">أعلى نقاط</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            total_teams = len(df_table)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_teams}</div>
                <div class="metric-label">عدد الفرق</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">⬇️</div>
                <div class="metric-label">الأخير: {df_table.iloc[-1]['الفريق']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("تعذر جلب بيانات الترتيب")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 1: المباريات
# ============================================================
with tabs[1]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📅 المباريات القادمة")
    t_search = st.text_input("🔍 ابحث عن فريق:", key="fixture_search")
    fixtures = get_fixtures(t_search)
    if fixtures:
        for i, m in enumerate(fixtures):
            st.markdown(f"""
            <div class="fixture-card">
                <span style="color: #00d4ff;">🏟️</span> {m}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("لا توجد مباريات مطابقة")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 2: اللاعبين
# ============================================================
with tabs[2]:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🏃 إحصائيات اللاعبين")
    p_input = st.text_input("🔍 ابحث عن لاعب (بالإنجليزية):", key="player_search", placeholder="مثال: Salah, Haaland, Saka...")
    if st.button("🔎 عرض الإحصائيات", key="player_btn"):
        if p_input:
            with st.spinner("جاري البحث..."):
                res, err = get_player_stats_fpl(p_input)
                if err:
                    st.error(err)
                else:
                    # عرض بطاقة اللاعب
                    st.markdown("---")
                    cols = st.columns(len(res))
                    icons = ["👤", "🏟️", "📍", "⚽", "🅰️", "⏱️", "⭐", "📊", "📈", "🛡️"]
                    for i, (k, v) in enumerate(res.items()):
                        with cols[i]:
                            icon = icons[i] if i < len(icons) else "📋"
                            st.markdown(f"""
                            <div class="metric-card">
                                <div style="font-size:1.5em">{icon}</div>
                                <div class="metric-value" style="font-size:1.3em">{v}</div>
                                <div class="metric-label">{k}</div>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("أدخل اسم لاعب للبحث")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TAB 3: غرفة التوقعات (المحاكاة)
# ============================================================
with tabs[3]:
    st.subheader("🧠 محرك المحاكاة المتقدم")
    st.markdown("*محاكاة مونت كارلو + توزيع بواسون لتوقع نتائج المباريات*")
    try:
        df = get_table()
        if df.empty:
            st.error("لا توجد بيانات للعمل عليها")
        else:
            teams = df['الفريق'].tolist()
            engine = PoissonEngine(df)
            simulator = MonteCarloSimulator(n_simulations=n_sims)

            st.markdown("---")
            col_h, col_a = st.columns(2)
            with col_h:
                h_team = st.selectbox("🏠 الفريق المضيف:", teams, index=0, key="sim_home")
                h_strength = engine.get_team_strength(h_team)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">القوة الهجومية: {h_strength['attack']:.2f}</div>
                    <div class="metric-label">القوة الدفاعية: {h_strength['defense']:.2f}</div>
                    <div class="metric-label">معدل النقاط: {h_strength['pts_rate']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_a:
                a_team = st.selectbox("✈️ الفريق الضيف:", teams, index=min(1, len(teams)-1), key="sim_away")
                a_strength = engine.get_team_strength(a_team)
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">القوة الهجومية: {a_strength['attack']:.2f}</div>
                    <div class="metric-label">القوة الدفاعية: {a_strength['defense']:.2f}</div>
                    <div class="metric-label">معدل النقاط: {a_strength['pts_rate']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)

            # حساب xG
            calc_h_xg, calc_a_xg = engine.calculate_xg(h_team, a_team, home_advantage)

            st.markdown("---")
            st.markdown("### ⚙️ تعديل الأهداف المتوقعة (xG)")
            xg_col1, xg_col2 = st.columns(2)
            with xg_col1:
                f_h_xg = st.slider(
                    f"xG {h_team}", 0.1, 5.0, float(calc_h_xg), 0.05,
                    key=f"xg_home_{h_team}_{a_team}"
    )
            with xg_col2:
                f_a_xg = st.slider(
                    f"xG {a_team}", 0.1, 5.0, float(calc_a_xg), 0.05,
                    key=f"xg_away_{h_team}_{a_team}"
    )

            st.markdown("---")
            if st.button(f"🚀 تشغيل محاكاة {n_sims:,} مباراة", use_container_width=True, key="run_sim"):
                with st.spinner(f"جاري تشغيل {n_sims:,} محاكاة..."):
                    sim_results = simulator.simulate_match(f_h_xg, f_a_xg)
                    # حفظ في session
                    st.session_state['last_sim'] = {
                        'h': h_team,
                        'a': a_team,
                        'results': sim_results,
                        'h_xg': f_h_xg,
                        'a_xg': f_a_xg
                    }
                    # عرض النتائج
                    st.markdown("### 📊 نتائج المحاكاة")
                    # احتمالات الفوز
                    r1, r2, r3 = st.columns(3)
                    with r1:
                        st.markdown(f"""
                        <div class="prob-home">
                            <div class="prob-value" style="color:#00c853">{sim_results['home_win_pct']}%</div>
                            <div style="color:#aaa; font-size:1.1em">فوز {h_team}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with r2:
                        st.markdown(f"""
                        <div class="prob-draw">
                            <div class="prob-value" style="color:#ffc107">{sim_results['draw_pct']}%</div>
                            <div style="color:#aaa; font-size:1.1em">تعادل</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with r3:
                        st.markdown(f"""
                        <div class="prob-away">
                            <div class="prob-value" style="color:#ff4444">{sim_results['away_win_pct']}%</div>
                            <div style="color:#aaa; font-size:1.1em">فوز {a_team}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    # النتيجة المتوقعة
                    most_likely = sim_results['most_likely_scores'][0][0]
                    st.markdown(f"""
                    <div style="text-align:center; margin:20px 0;">
                        <div class="score-display">{h_team} {most_likely} {a_team}</div>
                        <p style="color:#8888aa">النتيجة الأكثر احتمالاً</p>
                    </div>
                    """, unsafe_allow_html=True)
                    # إحصائيات إضافية
                    st.markdown("### 📈 إحصائيات متقدمة")
                    s1, s2, s3, s4 = st.columns(4)
                    with s1:
                        st.metric("⚽ متوسط الأهداف", sim_results['avg_total_goals'])
                    with s2:
                        st.metric("📊 أكثر من 2.5", f"{sim_results['over_25_pct']}%")
                    with s3:
                        st.metric("📉 أقل من 2.5", f"{sim_results['under_25_pct']}%")
                    with s4:
                        st.metric("⚽⚽ BTTS نعم", f"{sim_results['btts_yes_pct']}%")
                    # الرسوم البيانية
                    st.markdown("---")
                    chart_col1, chart_col2 = st.columns(2)
                    with chart_col1:
                        st.plotly_chart(
                            create_probability_chart(h_team, a_team, sim_results),
                            use_container_width=True
                        )
                    with chart_col2:
                        st.plotly_chart(
                            create_goals_distribution(h_team, a_team, sim_results),
                            use_container_width=True
                        )
                    # خريطة حرارية
                    st.plotly_chart(
                        create_score_heatmap(h_team, a_team, f_h_xg, f_a_xg),
                        use_container_width=True
                    )
                    # أكثر 10 نتائج احتمالاً
                    st.markdown("### 🎯 أكثر 10 نتائج احتمالاً")
                    score_df = pd.DataFrame(
                        sim_results['most_likely_scores'],
                        columns=['النتيجة', 'التكرار']
                    )
                    score_df['الاحتمال %'] = (score_df['التكرار'] / n_sims * 100).round(1)
                    score_df = score_df.drop('التكرار', axis=1)
                    st.dataframe(score_df, use_container_width=True)
    except Exception as e:
        st.error(f"❌ خطأ في المحرك: {e}")
        import traceback
        st.code(traceback.format_exc())

# ============================================================
# TAB 4: قناص القيمة
# ============================================================
with tabs[4]:
    st.subheader("🎯 كاشف رهانات القيمة (ValueBet Finder)")
    st.markdown("*قارن بين احتمالات النموذج واحتمالات السوق لاكتشاف فرص القيمة*")
    if 'last_sim' not in st.session_state:
        st.warning("⚠️ قم بتشغيل محاكاة في تبويب 'غرفة التوقعات' أولاً")
    else:
        sim = st.session_state['last_sim']
        results = sim['results']
        st.markdown(f"### 🏟️ {sim['h']} ضد {sim['a']}")
        st.markdown("---")
        st.markdown("#### 📥 أدخل احتمالات السوق (بالنسبة المئوية)")
        st.markdown("*يمكنك تحويل الأرجحية العشرية: مثلاً 2.50 = 40%*")
        vc1, vc2, vc3 = st.columns(3)
        with vc1:
            market_home = st.number_input(
                f"احتمال فوز {sim['h']} %",
                min_value=1.0, max_value=99.0, value=40.0, step=0.5, key="market_home"
            )
        with vc2:
            market_draw = st.number_input(
                "احتمال التعادل %",
                min_value=1.0, max_value=99.0, value=28.0, step=0.5, key="market_draw"
            )
        with vc3:
            market_away = st.number_input(
                f"احتمال فوز {sim['a']} %",
                min_value=1.0, max_value=99.0, value=32.0, step=0.5, key="market_away"
            )
        # أداة تحويل الأرجحية
        with st.expander("🔄 أداة تحويل الأرجحية"):
            dec_odds = st.number_input("أدخل الأرجحية العشرية:", min_value=1.01, max_value=100.0, value=2.50, step=0.01)
            implied = ValueBetFinder.implied_probability(dec_odds)
            st.info(f"الاحتمال الضمني: **{implied}%**")
        if st.button("🎯 تحليل القيمة", use_container_width=True, key="value_btn"):
            finder = ValueBetFinder()
            # تحليل كل نتيجة
            home_value = finder.find_value(results['home_win_pct'], market_home, min_edge)
            draw_value = finder.find_value(results['draw_pct'], market_draw, min_edge)
            away_value = finder.find_value(results['away_win_pct'], market_away, min_edge)
            st.markdown("---")
            st.markdown("### 📊 تقرير القيمة")
            v1, v2, v3 = st.columns(3)
            analyses = [
                (v1, f"فوز {sim['h']}", results['home_win_pct'], market_home, home_value),
                (v2, "تعادل", results['draw_pct'], market_draw, draw_value),
                (v3, f"فوز {sim['a']}", results['away_win_pct'], market_away, away_value),
            ]
            for col, label, model_p, market_p, value in analyses:
                with col:
                    edge_color = "#00ff88" if value['is_value'] else "#ff4444"
                    badge = "✅ VALUE BET!" if value['is_value'] else "❌ لا قيمة"
                    st.markdown(f"""
                    <div class="{'valuebet-alert' if value['is_value'] else 'glass-card'}">
                        <h4 style="color:white">{label}</h4>
                        <p>📊 النموذج: <b>{model_p}%</b></p>
                        <p>🏪 السوق: <b>{market_p}%</b></p>
                        <p style="color:{edge_color}; font-size:1.5em; font-weight:900">
                            الميزة: {value['edge']:+.1f}%
                        </p>
                        <p>📈 تصنيف القيمة: {value['value_rating']}%</p>
                        <p>💰 نسبة كيلي: {value['kelly_fraction']}%</p>
                        <p style="font-size:1.2em">{badge}</p>
                    </div>
                    """, unsafe_allow_html=True)
            # حفظ بيانات القيمة
            st.session_state['value_data'] = {
                'home_edge': home_value['edge'],
                'draw_edge': draw_value['edge'],
                'away_edge': away_value['edge']
            }
            # ملخص
            st.markdown("---")
            best_values = []
            if home_value['is_value']:
                best_values.append((f"فوز {sim['h']}", home_value['edge'], home_value['kelly_fraction']))
            if draw_value['is_value']:
                best_values.append(("تعادل", draw_value['edge'], draw_value['kelly_fraction']))
            if away_value['is_value']:
                best_values.append((f"فوز {sim['a']}", away_value['edge'], away_value['kelly_fraction']))
            if best_values:
                best = max(best_values, key=lambda x: x[1])
                st.success(f"""
                🎯 **أفضل فرصة قيمة:** {best[0]} | الميزة: {best[1]:+.1f}% | نسبة كيلي المقترحة: {best[2]}%
                """)
            else:
                st.warning("⚠️ لا توجد فرص قيمة واضحة في هذه المباراة بناءً على الحد الأدنى المحدد.")

# ============================================================
# TAB 5: الوكلاء AI
# ============================================================
with tabs[5]:
    st.subheader("🤖 نظام الوكلاء المتعددين (Multi-Agent AI)")
    st.markdown("*ثلاثة وكلاء ذكاء اصطناعي يعملون معاً لتقديم تحليل شامل*")
    if 'last_sim' not in st.session_state:
        st.warning("⚠️ قم بتشغيل محاكاة في تبويب 'غرفة التوقعات' أولاً")
    elif not api_key:
        st.warning("⚠️ أدخل مفتاح API في الشريط الجانبي")
    else:
        sim = st.session_state['last_sim']
        results = sim['results']
        st.markdown(f"### 🏟️ تحليل: {sim['h']} ضد {sim['a']}")
        st.markdown("---")
        # أخبار الكشّاف
        scout_news = st.text_area(
            "📰 أخبار إضافية (إصابات، غيابات، حالة الفريق):",
            placeholder="مثال: محمد صلاح مصاب في الكاحل، دي بروين عائد من الإيقاف...",
            key="scout_news"
        )
        # عرض الوكلاء
        agent_cols = st.columns(3)
        with agent_cols[0]:
            st.markdown("""
            <div class="agent-card agent-scout">
                <h4>🔍 وكيل الكشّاف</h4>
                <p style="color:#2196f3">تحليل البيانات الخام والإحصائيات</p>
            </div>
            """, unsafe_allow_html=True)
        with agent_cols[1]:
            st.markdown("""
            <div class="agent-card agent-tactician">
                <h4>🎯 وكيل التكتيكي</h4>
                <p style="color:#9c27b0">التحليل التكتيكي والسيناريوهات</p>
            </div>
            """, unsafe_allow_html=True)
        with agent_cols[2]:
            st.markdown("""
            <div class="agent-card agent-judge">
                <h4>⚖️ وكيل القاضي</h4>
                <p style="color:#ff9800">الحكم النهائي والتوصيات</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        if st.button("🚀 تشغيل نظام الوكلاء الكامل", use_container_width=True, key="run_agents"):
            agent_system = AgentSystem(api_key, ai_provider)
            # الوكيل 1: الكشّاف
            with st.spinner("🔍 وكيل الكشّاف يحلل البيانات..."):
                scout_report = agent_system.scout_agent(
                    sim['h'], sim['a'], results, scout_news
                )
            st.markdown("""
            <div class="agent-card agent-scout">
                <h4>🔍 تقرير الكشّاف</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(scout_report)
            st.session_state['scout_report'] = scout_report
            st.markdown("---")
            # الوكيل 2: التكتيكي
            with st.spinner("🎯 وكيل التكتيكي يحلل السيناريوهات..."):
                tactician_report = agent_system.tactician_agent(
                    sim['h'], sim['a'], results, scout_report
                )
            st.markdown("""
            <div class="agent-card agent-tactician">
                <h4>🎯 تقرير التكتيكي</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(tactician_report)
            st.session_state['tactician_report'] = tactician_report
            st.markdown("---")
            # الوكيل 3: القاضي
            with st.spinner("⚖️ وكيل القاضي يصدر حكمه النهائي..."):
                value_data = st.session_state.get('value_data', None)
                judge_report = agent_system.judge_agent(
                    sim['h'], sim['a'], results, scout_report, tactician_report, value_data
                )
            st.markdown("""
            <div class="agent-card agent-judge">
                <h4>⚖️ الحكم النهائي</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(judge_report)
            st.session_state['judge_report'] = judge_report
            # حفظ التقرير الكامل
            st.session_state['full_report'] = {
                'scout': scout_report,
                'tactician': tactician_report,
                'judge': judge_report,
                'match': f"{sim['h']} v {sim['a']}",
                'date': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
            # حفظ في السجل
            st.markdown("---")
            if 'last_sim' in st.session_state:
                save_cols = st.columns(2)
                with save_cols[0]:
                    actual_result = st.text_input(
                        "📝 النتيجة الفعلية (عند انتهاء المباراة):",
                        placeholder="مثال: 2-1",
                        key="actual_result"
                    )
                with save_cols[1]:
                    st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 حفظ التوقع في السجل", use_container_width=True, key="save_pred"):
                    s = st.session_state['last_sim']
                    predicted = s['results']['most_likely_scores'][0][0]
                    row = pd.DataFrame([{
                        "التاريخ": datetime.now().strftime("%Y-%m-%d"),
                        "المباراة": f"{s['h']} v {s['a']}",
                        "التوقع": predicted,
                        "النتيجة_الفعلية": actual_result if actual_result else "—",
                        "فوز_مضيف%": s['results']['home_win_pct'],
                        "تعادل%": s['results']['draw_pct'],
                        "فوز_ضيف%": s['results']['away_win_pct'],
                        "xG_مضيف": s['h_xg'],
                        "xG_ضيف": s['a_xg'],
                        "صحيح": "—"
                    }])
                    file_path = "prediction_history.csv"
                    row.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False)
                    st.toast("✅ تم حفظ التوقع!")
                    st.balloons()

# ============================================================
# TAB 6: سجل الدقة
# ============================================================
with tabs[6]:
    st.subheader("📈 سجل التوقعات وقياس الدقة")
    file_path = "prediction_history.csv"
    if os.path.exists(file_path):
        history_df = pd.read_csv(file_path)
        if not history_df.empty:
            # إحصائيات السجل
            total_preds = len(history_df)
            verified = history_df[history_df['النتيجة_الفعلية'] != '—']
            # حساب الدقة
            if len(verified) > 0:
                correct = verified[verified['التوقع'] == verified['النتيجة_الفعلية']]
                accuracy = len(correct) / len(verified) * 100
                # نتيجة قريبة (فارق هدف واحد أو أقل)
                close_correct = 0
                for _, row in verified.iterrows():
                    try:
                        pred_parts = str(row['التوقع']).split('-')
                        actual_parts = str(row['النتيجة_الفعلية']).split('-')
                        if len(pred_parts) == 2 and len(actual_parts) == 2:
                            diff = abs(int(pred_parts[0]) - int(actual_parts[0])) + \
                                   abs(int(pred_parts[1]) - int(actual_parts[1]))
                            if diff <= 1:
                                close_correct += 1
                    except:
                        pass
                close_accuracy = close_correct / len(verified) * 100
            else:
                accuracy = 0
                close_accuracy = 0
            # عرض الإحصائيات
            stat_cols = st.columns(4)
            with stat_cols[0]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_preds}</div>
                    <div class="metric-label">إجمالي التوقعات</div>
                </div>
                """, unsafe_allow_html=True)
            with stat_cols[1]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(verified)}</div>
                    <div class="metric-label">تم التحقق منها</div>
                </div>
                """, unsafe_allow_html=True)
            with stat_cols[2]:
                acc_color = "accuracy-good" if accuracy >= 40 else \
                            "accuracy-mid" if accuracy >= 25 else "accuracy-bad"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value {acc_color}">{accuracy:.1f}%</div>
                    <div class="metric-label">دقة النتيجة الصحيحة</div>
                </div>
                """, unsafe_allow_html=True)
            with stat_cols[3]:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{close_accuracy:.1f}%</div>
                    <div class="metric-label">دقة قريبة (±1 هدف)</div>
                </div>
                """, unsafe_allow_html=True)
            # الجدول
            st.markdown("---")
            st.markdown("### 📋 سجل التوقعات")
            # تعديل النتائج الفعلية
            edited_df = st.data_editor(
                history_df,
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "النتيجة_الفعلية": st.column_config.TextColumn(
                        "النتيجة الفعلية",
                        help="أدخل النتيجة الفعلية بصيغة: 2-1"
                    )
                }
            )
            # حفظ التعديلات
            btn_cols = st.columns(3)
            with btn_cols[0]:
                if st.button("💾 حفظ التعديلات", key="save_edits"):
                    # تحديث عمود "صحيح"
                    for idx, row in edited_df.iterrows():
                        if row['النتيجة_الفعلية'] != '—' and row['التوقع']:
                            edited_df.at[idx, 'صحيح'] = \
                                '✅' if row['التوقع'] == row['النتيجة_الفعلية'] else '❌'
                    edited_df.to_csv(file_path, index=False)
                    st.toast("✅ تم حفظ التعديلات!")
                    st.rerun()
            with btn_cols[1]:
                csv = history_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    "📥 تصدير CSV",
                    csv,
                    "valuebet_history.csv",
                    "text/csv",
                    key="download_history"
                )
            with btn_cols[2]:
                if st.button("🗑️ مسح السجل بالكامل", key="clear_history"):
                    os.remove(file_path)
                    st.toast("🗑️ تم مسح السجل!")
                    st.rerun()
        else:
            st.markdown("""
            <div class="glass-card" style="text-align:center; padding:60px;">
                <div style="font-size:4em">📭</div>
                <h3 style="color:#8888aa">السجل فارغ حالياً</h3>
                <p style="color:#666">قم بتشغيل محاكاة وحفظ التوقعات لبناء سجل الدقة</p>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# Footer
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align:center; padding:20px; color:#444;">
    <p>⚽ <b>ValueBet Pro Analytics v3.0</b> | محرك بواسون + مونت كارلو + وكلاء AI</p>
    <p style="font-size:0.8em">⚠️ هذه أداة تحليلية تعليمية. جميع التوقعات احتمالية وليست مضمونة.</p>
</div>
""", unsafe_allow_html=True)
