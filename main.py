try:
    print("=== DEBUG: Počinjem API zahtev ===")
    print(f"XAI_API_KEY dužina: {len(XAI_API_KEY)} karaktera")
    print(f"XAI_API_KEY prvih 10: {XAI_API_KEY[:10]}...")
    print(f"XAI_API_KEY poslednjih 10: {...XAI_API_KEY[-10:]}")

    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    print("Headers koji se šalju:")
    for k, v in headers.items():
        print(f"  {k}: {v[:20]}... (skrati za log)")

    print("Data/prompt koji šaljemo (prvih 200 karaktera):")
    print(str(data)[:200] + "...")

    resp = requests.post(url, headers=headers, json=data, timeout=30)
    print(f"API status code: {resp.status_code}")
    print(f"API response headers: {resp.headers}")
    print(f"Raw API response (ceo, prvih 500 karaktera):")
    print(resp.text[:500] + "..." if len(resp.text) > 500 else resp.text)

    if resp.status_code != 200:
        print("API NIJE 200 – preskačem parsovanje")
        continue

    try:
        result_json = resp.json()
        print("JSON uspešno parsovan!")
        print(f"JSON sadržaj (prvih 200 karaktera): {str(result_json)[:200]}...")
    except Exception as json_err:
        print(f"JSON parsovanje ipak palo: {str(json_err)}")
        print("Raw text koji je pao: " + resp.text[:300])
        continue

    result = result_json["choices"][0]["message"]["content"].strip()
    print(f"Result sadržaj (prvih 100 karaktera): {result[:100]}...")

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
    print(f"Glavna greška u hunter_cycle: {str(e)}")
    print(f"Full exception info: {repr(e)}")
    if 'resp' in locals():
        print(f"Status pre greške: {resp.status_code}")
        print(f"Raw response pre greške: {resp.text[:300]}...")
