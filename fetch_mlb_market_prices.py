
import requests
import json

url = "https://smp.ks.sportsbook.fanduel.com/api/sports/fixedodds/readonly/v1/getMarketPrices?priceHistory=1"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://sportsbook.fanduel.com",
    "referer": "https://sportsbook.fanduel.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}

payload = {
  "marketIds": [
    "720.121831340",
    "720.121827296",
    "720.121831339",
    "720.121822262",
    "720.121750208",
    "720.121822260",
    "720.121804835",
    "720.121750001",
    "720.121804831",
    "720.121804917",
    "720.121750014",
    "720.121804915",
    "720.121805528",
    "720.121750017",
    "720.121805527",
    "720.121805165",
    "720.121750179",
    "720.121805161",
    "720.121805646",
    "720.121750211",
    "720.121805649",
    "720.121807349",
    "720.121750034",
    "720.121807348",
    "720.121807369",
    "720.121749955",
    "720.121807370",
    "720.121807447",
    "720.121749961",
    "720.121807448",
    "720.121821002",
    "720.121749964",
    "720.121821004",
    "720.121828547",
    "720.121750168",
    "720.121828553",
    "720.121829377",
    "720.121750170",
    "720.121829372",
    "720.121842477",
    "720.121749953",
    "720.121842473",
    "720.121807722",
    "720.121750186",
    "720.121807728",
    "720.121807763",
    "720.121750184",
    "720.121807761"
  ]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    with open("mlb_market_prices.json", "w") as out_file:
        json.dump(data, out_file, indent=2)
    print("MLB market prices saved to mlb_market_prices.json")
else:
    print("Failed to fetch market prices:", response.status_code)
