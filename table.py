import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import re  # أضفنا مكتبة التعابير النمطية

link = "https://onefootball.com/en/competition/premier-league-9/table"

# إضافة ترويسة لتبدو كمتصفح حقيقي وتتجنب الحظر
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

source = requests.get(link, headers=headers).text
page = BeautifulSoup(source, "lxml")

# إعداد أنماط بحث مرنة تتجاهل الرموز العشوائية في نهاية الكلاس
row_pattern = re.compile(r"standings__row", re.IGNORECASE)
cell_pattern = re.compile(r"standings__cell", re.IGNORECASE)
team_pattern = re.compile(r"standings__teamName", re.IGNORECASE)

# البحث باستخدام النمط المرن بدلاً من الاسم الحرفي
rows = page.find_all("li", class_=row_pattern)

table = [["Position", "Team", "Played", "Wins", "Draws", "Losses", "Goal Difference", "Points"]]

for row in rows:
    position_elem = row.find("div", class_=cell_pattern)
    team_elem = row.find(["p", "span", "div"], class_=team_pattern) # جعلنا وسم الفريق مرناً أيضاً
    stats = row.find_all("div", class_=cell_pattern)

    # التأكد من وجود العناصر لتجنب أخطاء (NoneType)
    if position_elem and team_elem and len(stats) >= 8:
        position = position_elem.text.strip()
        team = team_elem.text.strip()
        played = stats[2].text.strip()
        wins = stats[3].text.strip()
        draws = stats[4].text.strip()
        losses = stats[5].text.strip()
        goal_difference = stats[6].text.strip()
        points = stats[7].text.strip()

        table.append([position, team, played, wins, draws, losses, goal_difference, points])

print(tabulate(table, headers="firstrow", tablefmt="grid"))
