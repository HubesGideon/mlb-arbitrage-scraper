import requests
import json
from datetime import datetime

FANDUEL_URL = "https://smp.ks.sportsbook.fanduel.com/api/sports/fixedodds/readonly/v1/getMarketPrices?priceHistory=1"
FANDUEL_MARKET_IDS = [
    "720.121831340", "720.121827296", "720.121831339", "720.121822262", "720.121750208",
]

DRAFTKINGS_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/84240?category=game-lines&subcategory=moneyline"

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://sportsbook.fanduel.com",
    "referer": "https://sportsbook.fanduel.com/",
    "user-agent": "Mozilla/5.0"
}

def get_fanduel_odds():
    payload = {"marketIds": FANDUEL_MARKET_IDS}
    response = requests.post(FANDUEL_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"[FANDUEL ERROR] Status code: {response.status_code}")
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
            "teamB_odds": team_b_odds,
            "book": "FanDuel"
        }
        matchups.append(matchup)
    return matchups

def get_draftkings_odds():
    response = requests.get(DRAFTKINGS_URL)
    if response.status_code != 200:
        print(f"[DRAFTKINGS ERROR] Status code: {response.status_code}")
        return []
    data = response.json()
    events = {event['eventId']: event for event in data['eventGroup']['events']}
    markets = data['eventGroup']['offerCategories'][0]['offerSubcategory']['offers']
    matchups = []
    for game in markets:
        if len(game) == 0:
            continue
        market = game[0]  # moneyline market
        outcomes = market.get("outcomes", [])
        if len(outcomes) != 2:
            continue
        try:
            team_a = outcomes[0]
            team_b = outcomes[1]
            matchup = {
                "marketId": market.get("label", "draftkings_ml"),
                "teamA_id": team_a["participant"] + "_DK",
                "teamB_id": team_b["participant"] + "_DK",
                "teamA_odds": team_a["oddsDecimal"] or 0,
                "teamB_odds": team_b["oddsDecimal"] or 0,
                "book": "DraftKings"
            }
            matchups.append(matchup)
        except (KeyError, TypeError):
            continue
    return matchups

def detect_arbitrage(matchups):
    arbitrage_opps = []
    for i, match_a in enumerate(matchups):
        for match_b in matchups[i+1:]:
            if match_a["teamA_id"] == match_b["teamB_id"] and match_a["teamB_id"] == match_b["teamA_id"]:
                implied_prob = 1 / match_a["teamA_odds"] + 1 / match_b["teamA_odds"]
                if implied_prob < 1:
                    arbitrage_opps.append({
                        "matchup": (match_a["teamA_id"], match_a["teamB_id"]),
                        "bookA": match_a["book"],
                        "oddsA": match_a["teamA_odds"],
                        "bookB": match_b["book"],
                        "oddsB": match_b["teamA_odds"],
                        "edge": round(1 - implied_prob, 4)
                    })
    return arbitrage_opps

def log_arbitrage(opps):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("arbitrage_log.txt", "a") as f:
        for opp in opps:
            line = (
                f"[{timestamp}] Arbitrage between {opp['bookA']} and {opp['bookB']}! "
                f"{opp['matchup'][0]} vs {opp['matchup'][1]} | Odds: {opp['oddsA']} vs {opp['oddsB']} "
                f"| Edge: {opp['edge']*100:.2f}%\n"
            )
            print(line.strip())
            f.write(line)

def send_alert(opps):
    # Placeholder - hook this into email, Slack, Discord, etc.
    pass

def main():
    print("[INFO] Fetching odds from sportsbooks...")
    fd_odds = get_fanduel_odds()
    dk_odds = get_draftkings_odds()
    all_odds = fd_odds + dk_odds

    if not all_odds:
        print("[INFO] No matchups found.")
        return

    arbitrage_opps = detect_arbitrage(all_odds)
    if arbitrage_opps:
        log_arbitrage(arbitrage_opps)
        send_alert(arbitrage_opps)
    else:
        print("[INFO] No arbitrage opportunities at this time.")

if __name__ == "__main__":
    main()
