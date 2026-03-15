from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from googlesearch import search  

app = Flask(__name__)

# إضافة ترويسة موحدة لجميع الطلبات لتبدو كمتصفح حقيقي وتتجنب الحظر
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

@app.route('/')
def index():
    return "Hey there! Welcome to the Premier League API 2.0 \n\n you can use the following endpoints:\n\n /players/<player_name> \n /fixtures \n /fixtures/<team> \n /table \n\n Enjoy!"

@app.route('/players/<player_name>', methods=['GET'])
def get_player(player_name):
    try:
        # Use Google search to find the player's stats page
        query = f"{player_name} premier league.com stats"
        search_results = list(search(query, num_results=5))
        if search_results:
            res = search_results[0]
        else:
            return jsonify({"error": "No search results found for the query."}), 404

        # Adjust the URL to point to the stats page
        if "stats" in res:
            res = res.replace('stats', 'overview')
        sta = res.replace('overview', 'stats')

        # Fetch the stats page
        source = requests.get(sta, headers=HEADERS).text
        page = BeautifulSoup(source, "lxml")

        # Extract player details safely
        name_elem = page.find("div", class_="player-header__name t-colour")
        name = name_elem.text.strip() if name_elem else "Unknown"

        position_label = page.find("div", class_="player-overview__label", string="Position")
        position = position_label.find_next_sibling("div", class_="player-overview__info").text.strip() if position_label else "Unknown"

        # Extract club information
        club = "No longer part of EPL"
        if "Club" in page.text:
            club_info = page.find_all("div", class_="info")
            if len(club_info) > 0:
                club = club_info[0].text.strip()

        # Extract detailed stats
        detailed_stats = {}
        stat_elements = page.find_all("div", class_="player-stats__stat-value")
        for stat in stat_elements:
            stat_title = stat.text.split("\n")[0].strip()
            stat_value_elem = stat.find("span", class_="allStatContainer")
            stat_value = stat_value_elem.text.strip() if stat_value_elem else "N/A"
            detailed_stats[stat_title] = stat_value

        # Extract personal details
        source2 = requests.get(res, headers=HEADERS).text
        page2 = BeautifulSoup(source2, "lxml")
        personal_details = page2.find("div", class_="player-info__details-list")

        nationality = "Unknown"
        dob = "Unknown"
        height = "Unknown"

        if personal_details:
            nationality_elem = personal_details.find("span", class_="player-info__player-country")
            nationality = nationality_elem.text.strip() if nationality_elem else "Unknown"

            dob_info = personal_details.find_all("div", class_="player-info__col")
            for info in dob_info:
                label_elem = info.find("div", class_="player-info__label")
                if label_elem:
                    label = label_elem.text.strip()
                    if label == "Date of Birth":
                        val = info.find("div", class_="player-info__info")
                        dob = val.text.strip() if val else "Unknown"
                    elif label == "Height":
                        val = info.find("div", class_="player-info__info")
                        height = val.text.strip() if val else "Unknown"

        return jsonify({
            "name": name,
            "position": position,
            "club": club,
            "key_stats": detailed_stats,
            "Nationality": nationality,
            "Date of Birth": dob,
            "Height": height
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/fixtures')
def fixtures_list():
    try:
        link = "https://onefootball.com/en/competition/premier-league-9/fixtures"
        source = requests.get(link, headers=HEADERS).text
        page = BeautifulSoup(source, "lxml")
        
        # استخدام نمط مرن لكشط المباريات
        match_pattern = re.compile(r"matchCard", re.IGNORECASE)
        fix = page.find_all("a", class_=match_pattern)

        fixtures = []
        for match in fix:
            fixture = match.get_text(separator=" ").strip()
            fixtures.append(fixture)

        return jsonify({"fixtures": fixtures})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/fixtures/<team>', methods=['GET'])
def get_fixtures(team):
    try:
        link = "https://onefootball.com/en/competition/premier-league-9/fixtures"
        source = requests.get(link, headers=HEADERS).text
        page = BeautifulSoup(source, "lxml")
        
        # استخدام نمط مرن لكشط المباريات
        match_pattern = re.compile(r"matchCard", re.IGNORECASE)
        fix = page.find_all("a", class_=match_pattern)

        fixtures = []
        for match in fix:
            fixture = match.get_text(separator=" ").strip()
            fixtures.append(fixture)

        filtered_fixtures = [fixture for fixture in fixtures if team.lower() in fixture.lower()]

        return jsonify({"team_fixtures": filtered_fixtures})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/table')
def table():
    try:
        link = "https://onefootball.com/en/competition/premier-league-9/table"
        source = requests.get(link, headers=HEADERS).text
        page = BeautifulSoup(source, "lxml")

        # استخدام أنماط مرنة لكشط الجدول
        row_pattern = re.compile(r"standings__row", re.IGNORECASE)
        cell_pattern = re.compile(r"standings__cell", re.IGNORECASE)
        team_pattern = re.compile(r"standings__teamName", re.IGNORECASE)

        rows = page.find_all("li", class_=row_pattern)

        table_data = []
        table_data.append(["Position", "Team", "Played", "Wins", "Draws", "Losses", "Goal Difference", "Points"])

        for row in rows:
            position_elem = row.find("div", class_=cell_pattern)
            team_elem = row.find(["p", "span", "div"], class_=team_pattern)
            stats = row.find_all("div", class_=cell_pattern)

            if position_elem and team_elem and len(stats) >= 8:
                position = position_elem.text.strip()
                team = team_elem.text.strip()
                played = stats[2].text.strip()
                wins = stats[3].text.strip()
                draws = stats[4].text.strip()
                losses = stats[5].text.strip()
                goal_difference = stats[6].text.strip()
                points = stats[7].text.strip()

                table_data.append([position, team, played, wins, draws, losses, goal_difference, points])

        return jsonify({"table": table_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ =="__main__":
    app.run(debug=True)

