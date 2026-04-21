import cloudscraper, json, time
s = cloudscraper.create_scraper()
for i in range(3):
    r = s.post("https://api.smspool.net/purchase/sms", data={
        "key": "jCQH7hDydYjVxO8449OKru8HOsR22eJ1",
        "country": "ES", "service": "457", "pricing_option": "0"
    })
    d = json.loads(r.text)
    if d.get("success"):
        phone = d["phonenumber"]
        oid = d["orderid"]
        bal = d["current_balance"]
        print(f"+34 {phone} | Order: {oid} | Saldo: ${bal}")
    else:
        print(f"ERROR: {d}")
    time.sleep(1)
