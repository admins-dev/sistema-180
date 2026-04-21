"""
Ghost Mouse - Diagnostico completo de proxies.
Verifica conexion, geo-localizacion, y acceso a Instagram por cada proxy.
"""
import requests
import time

PROXIES = [
    {"name": "Laura", "server": "46.34.42.14:12323", "user": "14a407c433ed4", "pwd": "60852e0bba"},
    {"name": "Carlos", "server": "213.220.30.200:12323", "user": "14a407c433ed4", "pwd": "60852e0bba"},
    {"name": "Ana", "server": "213.220.27.116:12323", "user": "14a407c433ed4", "pwd": "60852e0bba"},
    {"name": "Pablo", "server": "213.220.22.110:12323", "user": "14a407c433ed4", "pwd": "60852e0bba"},
    {"name": "Marta", "server": "213.220.23.188:12323", "user": "14a407c433ed4", "pwd": "60852e0bba"},
]

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"


def test_proxy(p):
    name = p["name"]
    proxy_url = "http://{}:{}@{}".format(p["user"], p["pwd"], p["server"])
    proxies = {"http": proxy_url, "https": proxy_url}

    print("\n--- {} ({}) ---".format(name, p["server"]))

    # Test 1: Conexion basica
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
        data = r.json()
        ip = data["origin"].split(",")[0].strip()
        print("  [1] IP via proxy: {}".format(ip))
    except Exception as e:
        print("  [1] ERROR conexion: {}".format(e))
        return {"name": name, "status": "DEAD", "error": str(e)}

    # Test 2: Geo-location
    try:
        geo = requests.get("http://ip-api.com/json/{}".format(ip), timeout=5).json()
        city = geo.get("city", "?")
        country = geo.get("country", "?")
        isp = geo.get("isp", "?")
        hosting = geo.get("hosting", False)
        print("  [2] Ubicacion: {} / {} / ISP: {}".format(city, country, isp))
        if hosting:
            print("      [WARN] IP de DATACENTER - Instagram la detecta!")
        else:
            print("      [OK] IP residencial - buena para Instagram")
    except Exception as e:
        city, country, isp, hosting = "?", "?", "?", True
        print("  [2] ERROR geo: {}".format(e))

    # Test 3: Acceso a Instagram
    try:
        headers = {"User-Agent": UA}
        r = requests.get("https://www.instagram.com/", proxies=proxies, headers=headers, timeout=15, allow_redirects=True)
        status = r.status_code
        print("  [3] Instagram HTTP: {}".format(status))

        if status == 200:
            if "login" in r.text[:500].lower() or "instagram" in r.text[:500].lower():
                print("      [OK] Instagram ACCESIBLE")
            else:
                print("      [?] Respuesta rara")
        elif status == 429:
            print("      [BLOCK] Rate limited!")
        elif status == 403:
            print("      [BLOCK] IP bloqueada!")
        else:
            print("      [?] Status inesperado")
    except Exception as e:
        status = 0
        print("  [3] ERROR Instagram: {}".format(e))

    return {
        "name": name,
        "ip": ip,
        "city": city,
        "country": country,
        "isp": isp,
        "datacenter": hosting,
        "ig_status": status,
        "status": "OK" if status == 200 and not hosting else "WARN" if status == 200 else "FAIL"
    }


def main():
    print("=" * 70)
    print("  DIAGNOSTICO COMPLETO DE PROXIES")
    print("=" * 70)

    results = []
    for p in PROXIES:
        res = test_proxy(p)
        results.append(res)
        time.sleep(1)

    # Tu IP real (sin proxy)
    print("\n--- TU IP REAL (sin proxy) ---")
    try:
        r = requests.get("http://httpbin.org/ip", timeout=5)
        ip = r.json()["origin"]
        geo = requests.get("http://ip-api.com/json/{}".format(ip), timeout=5).json()
        print("  IP: {}".format(ip))
        print("  Ubicacion: {} / {} / ISP: {}".format(
            geo.get("city", "?"), geo.get("country", "?"), geo.get("isp", "?")))
    except Exception as e:
        print("  ERROR: {}".format(e))

    # Resumen
    print("\n" + "=" * 70)
    print("  RESUMEN")
    print("=" * 70)
    for r in results:
        status = r.get("status", "?")
        dc = " [DATACENTER!]" if r.get("datacenter") else " [RESIDENCIAL]"
        icon = "[OK]" if status == "OK" else "[WARN]" if status == "WARN" else "[FAIL]"
        print("  {} {} -> {} / {} / IG:{}{}".format(
            icon, r.get("name", "?"), r.get("ip", "?"),
            r.get("city", "?"), r.get("ig_status", "?"), dc))

    dc_count = len([r for r in results if r.get("datacenter")])
    if dc_count > 0:
        print("\n  [!!!] {} de 5 proxies son de DATACENTER".format(dc_count))
        print("  Instagram detecta IPs de datacenter y bloquea el login.")
        print("  SOLUCION: Usar proxies RESIDENCIALES (ej: Bright Data, IPRoyal)")
    else:
        print("\n  Todos los proxies son residenciales. El problema puede ser otro.")


if __name__ == "__main__":
    main()
