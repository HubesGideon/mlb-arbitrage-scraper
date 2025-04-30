print("[DEBUG] Script started", flush=True)

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
    print("[DEBUG] Getting FanDuel odds...", flush=True)
    payload = {"marketIds": FANDUEL_MARKET_IDS}
    response = requests.post(FANDUEL_URL, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"[FANDUEL ERROR] Status code: {response.status_code}", flush=True)
        return []
    odds_data = response.json()
    print(json.dumps(odds_data, indent=2)[:1000], flush=True)  # Truncated for stability
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
    print(f"[DEBUG] Found {len(matchups)} FanDuel matchups", flush=True)
    return matchups


DK_HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "referer": "https://sportsbook.draftkings.com/"
}

def get_draftkings_odds():
    print("[DEBUG] Getting DraftKings odds...", flush=True)
    try:
        response = requests.get(DRAFTKINGS_URL, headers=DK_HEADERS)
        print(f"[DEBUG] DraftKings status: {response.status_code}, content-type: {response.headers.get('Content-Type')}", flush=True)
        if response.status_code != 200:
            print(f"[DRAFTKINGS ERROR] Status code: {response.status_code}", flush=True)
            return []
        print(f"[DEBUG] DraftKings raw response: {response.text[:1000]}", flush=True)
        data = response.json()  # Truncated for stability
        return []  # Temporarily disable parsing to test structure
    except Exception as e:
        print(f"[DRAFTKINGS ERROR] Exception occurred: {e}", flush=True)
        return []

def main():
    try:
        print("[DEBUG] Entered main()", flush=True)
        fd_odds = get_fanduel_odds()
        print(f"[DEBUG] Total FanDuel odds: {len(fd_odds)}", flush=True)
        dk_odds = get_draftkings_odds()
        print(f"[DEBUG] Total DraftKings odds: {len(dk_odds)}", flush=True)
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}", flush=True)

if __name__ == "__main__":
    main()
