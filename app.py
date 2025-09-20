import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_bbc_table():
    url = "https://www.bbc.com/sport/football/premier-league/table"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = []
    rows = soup.select("table.gs-o-table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 10:  # نتأكد إن فيه بيانات
            position = cols[0].text.strip()
            team = cols[1].text.strip()
            played = cols[2].text.strip()
            wins = cols[3].text.strip()
            draws = cols[4].text.strip()
            losses = cols[5].text.strip()
            goals_for = cols[6].text.strip()
            goals_against = cols[7].text.strip()
            goal_diff = cols[8].text.strip()
            points = cols[9].text.strip()

            table.append([position, team, played, wins, draws, losses, goals_for, goals_against, goal_diff, points])

    return pd.DataFrame(table, columns=["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"])


def fetch_sky_table():
    url = "https://www.skysports.com/premier-league-table"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = []
    rows = soup.select("table.standing-table__table tbody tr")

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 10:
            position = cols[0].text.strip()
            team = cols[1].text.strip()
            played = cols[2].text.strip()
            wins = cols[3].text.strip()
            draws = cols[4].text.strip()
            losses = cols[5].text.strip()
            goals_for = cols[6].text.strip()
            goals_against = cols[7].text.strip()
            goal_diff = cols[8].text.strip()
            points = cols[9].text.strip()

            table.append([position, team, played, wins, draws, losses, goals_for, goals_against, goal_diff, points])

    return pd.DataFrame(table, columns=["Pos", "Team", "P", "W", "D", "L", "GF", "GA", "GD", "Pts"])


if __name__ == "__main__":
    print("BBC Sport Table:")
    print(fetch_bbc_table())
    print("\nSky Sports Table:")
    print(fetch_sky_table())
