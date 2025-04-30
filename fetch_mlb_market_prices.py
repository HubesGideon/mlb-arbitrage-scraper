import requests
import json
from datetime import datetime

FANDUEL_URL = "https://smp.ks.sportsbook.fanduel.com/api/sports/fixedodds/readonly/v1/getMarketPrices?priceHistory=1"
MARKET_IDS = [
    "720.121831340", "720.121827296", "720.121831339", "720.121822262", "720.121750208",
    # (Add more marketIds or load from a file/database)
]

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://sportsbook.fanduel.com",
    "referer": "https://sportsbook.fanduel.com/",
    "user-agent": "Mozilla/5.0"
}

def get_fanduel_odds():
    payload = {"marketIds": MARKET_IDS}
    response = requests.post(FANDUEL_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print(f"[ERROR] Status code: {response.status_code}")
        return []

    odds_data = response.json()
    matchups = []

    for market in odds_data:
        if market["marketStatus"] != "OPEN":
            continue

        runners = market.get("runnerDetails", [])
        if len(runners) != 2:
            continue

        try:
            team_a_odds = runners[0]["winRunnerOdds"]["trueOdds"]["decimalOdds"]["decimalOdds"]
            team_b_odds = runners[1]["winRunnerOdds"]["trueOdds"]["decimalOdds"]["decimalOdds"]
        except (KeyError, TypeError):
            continue

        matchup = {
            "marketId": market["marketId"],
            "teamA_id": runners[0]["selectionId"],
            "teamB_id": runners[1]["selectionId"],
            "teamA_odds": team_a_odds,
            "teamB_odds": team_b_odds
        }
        matchups.append(matchup)

    return matchups

def detect_arbitrage(matchups):
    arbitrage_opps = []
    for match in matchups:
        implied_prob = 1 / match["teamA_odds"] + 1 / match["teamB_odds"]
        if implied_prob < 1:
            match["edge"] = round(1 - implied_prob, 4)
            arbitrage_opps.append(match)
    return arbitrage_opps

def log_arbitrage(opps):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("arbitrage_log.txt", "a") as f:
        for opp in opps:
            line = f"[{timestamp}] Arbitrage found! Market {opp['marketId']} | A: {opp['teamA_odds']} vs B: {opp['teamB_odds']} | Edge: {opp['edge']*100:.2f}%\n"
            print(line.strip())
            f.write(line)

def send_alert(opps):
    # Placeholder - hook this into email, Slack, Discord, etc.
    pass

def main():
    print("[INFO] Fetching FanDuel odds...")
    matchups = get_fanduel_odds()
    if not matchups:
        print("[INFO] No matchups found.")
        return

    arbitrage_opps = detect_arbitrage(matchups)
    if arbitrage_opps:
        log_arbitrage(arbitrage_opps)
        send_alert(arbitrage_opps)
    else:
        print("[INFO] No arbitrage opportunities at this time.")

if __name__ == "__main__":
    main()
