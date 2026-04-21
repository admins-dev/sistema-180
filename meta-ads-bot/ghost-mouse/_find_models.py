import requests
r = requests.get("https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyAJt3YzfhP-r6jxMkoPZyCjtbF1Sy2wiWk")
data = r.json()
for m in data.get("models", []):
    name = m["name"]
    display = m.get("displayName", "")
    if any(k in name.lower() + display.lower() for k in ["image", "banana", "imagen", "nano"]):
        methods = [mm.split("/")[-1] for mm in m.get("supportedGenerationMethods", [])]
        print(f"{name} -> {display} | methods: {methods}")
