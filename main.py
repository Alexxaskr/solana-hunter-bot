import os
import time
import requests
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
XAI_API_KEY = os.getenv("XAI_API_KEY")

HANDLES = [
    "solanamobile", "mattlefun", "bonkfun", "JupiterExchange", "Backpack",
    "binance", "okx", "MEXC_Global", "Bybit_Official", "solana", "marginfi",
    "driftprotocol", "raydium", "phantom", "Helium", "pumpdotfun",
    "MEXC_Official", "KuCoin", "gate_io", "Crypto_com", "orca_so",
    "meteoraAG", "kamino_finance", "MagicEden", "Jito_sol", "solendprotocol",
    "cherrydotfun", "hyperliquidxyz", "ethena_labs", "redstone_defi",
    "SuiNetwork", "Aptos_Network", "grass_foundation"
]

seen_post_ids = set()

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    resp = requests.post(url, json=payload)
    print(f"Telegram: {resp.status_code}")

def hunter_cycle():
    prompt = f"""
Ti si Solana Hunter. Koristi x_search (Latest, max 30 min) SAMO iz: {', '.join(HANDLES)}.

Traži: airdrop OR giveaway OR campaign OR unlock OR "token unlock" OR vesting OR listing OR "new listing".

Filteri: -filter:replies min_faves:5 -scam -fake -rug.

Ako imaš NOV post, napravi JEDNU poruku:
🚨 [KATEGORIJA] – @handle

Opis.

👇 <a href="https://x.com/handle/status/POST_ID">Open on X</a>

Ako nema – SAMO: NO_NEW_ALERTS
"""

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-4-fast-non-reasoning",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "tools": [{"type": "x_search"}]
    }

    try:
        print("=== DEBUG: Počinjem API zahtev ===")
        print(f"XAI_API_KEY dužina: {len(XAI_API_KEY)} karaktera")
        print(f"XAI_API_KEY prvih 10: {XAI_API_KEY[:10]}...")
        print(f"XAI_API_KEY poslednjih 10: {XAI_API_KEY[-10:]}")

        print("Headers koji se šalju:")
        for k, v in headers.items():
            print(f"  {k}: {v[:20]}...")

        print("Prompt prvih 200 karaktera:")
        print(prompt[:200] + "...")

        resp = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"API status code: {resp.status_code}")
        print(f"Raw API response (prvih 500 karaktera):")
        print(resp.text[:500] + "..." if len(resp.text) > 500 else resp.text)

        if resp.status_code != 200:
            print("API NIJE 200 – preskačem")
            return

        result_json = resp.json()
        print("JSON uspešno parsovan!")
        result = result_json["choices"][0]["message"]["content"].strip()

        if "NO_NEW_ALERTS" not in result.upper():
            print("Pronađen alert – šaljem na Telegram")
            for msg in result.split("\n\n"):
                if "https://x.com" in msg:
                    post_id = msg.split("status/")[-1].split('"')[0] if "status/" in msg else ""
                    if post_id and post_id not in seen_post_ids:
                        seen_post_ids.add(post_id)
                        send_to_telegram(msg.strip())
                        print(f"Poslan alert: {post_id}")
        else:
            print("Nema novih.")
    except Exception as e:
        print(f"Greška u hunter_cycle: {str(e)}")
        if 'resp' in locals():
            print(f"Status pre greške: {resp.status_code}")
            print(f"Raw response pre greške: {resp.text[:300]}...")

print("Hunter radi...")
while True:
    hunter_cycle()
    time.sleep(300)
