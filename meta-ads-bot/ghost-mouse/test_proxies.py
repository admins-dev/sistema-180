"""Verificar que los 5 proxies de IPRoyal funcionan."""
import requests

PROXIES = [
    {"ip": "46.34.42.14", "port": "12323", "user": "14a407c433ed4", "pass": "60852e0bba"},
    {"ip": "213.220.30.200", "port": "12323", "user": "14a407c433ed4", "pass": "60852e0bba"},
    {"ip": "213.220.27.116", "port": "12323", "user": "14a407c433ed4", "pass": "60852e0bba"},
    {"ip": "213.220.22.110", "port": "12323", "user": "14a407c433ed4", "pass": "60852e0bba"},
    {"ip": "213.220.23.188", "port": "12323", "user": "14a407c433ed4", "pass": "60852e0bba"},
]

for i, p in enumerate(PROXIES, 1):
    proxy_url = f"http://{p['user']}:{p['pass']}@{p['ip']}:{p['port']}"
    try:
        r = requests.get("https://ipinfo.io/json", proxies={"http": proxy_url, "https": proxy_url}, timeout=15)
        data = r.json()
        ip = data.get("ip", "?")
        city = data.get("city", "?")
        country = data.get("country", "?")
        org = data.get("org", "?")
        print(f"Proxy {i}: OK | IP: {ip} | {city}, {country} | {org}")
    except Exception as e:
        print(f"Proxy {i}: FALLO | {e}")
