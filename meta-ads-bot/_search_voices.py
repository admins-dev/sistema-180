import requests

r = requests.get(
    "https://api.elevenlabs.io/v1/shared-voices",
    params={"page_size": 20, "search": "jarvis"},
    timeout=10,
)
voices = r.json().get("voices", [])
for v in voices[:15]:
    vid = v.get("voice_id", "")
    name = v.get("name", "")
    accent = v.get("accent", "")
    desc = v.get("description", "")[:100]
    use_count = v.get("cloned_by_count", 0)
    print(f"{vid} | {name} | {accent} | uses:{use_count} | {desc}")
