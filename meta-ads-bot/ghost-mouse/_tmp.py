import requests, json
key = "AIzaSyAJt3YzfhP-r6jxMkoPZyCjtbF1Sy2wiWk"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-pro-preview:generateContent?key={key}"

prompt = """Eres un experto en ventas B2B por Instagram DM. Escribe un DM de Instagram para este negocio ofreciendo marketing digital.

Negocio: Daniel Veiga Vitale Hair & Beauty  
Ciudad: Malaga  
Tipo: peluqueria  

REGLAS: Maximo 3 frases. Tono casual. Sin emojis excesivos. Español de España.
Escribe SOLO el mensaje final, sin explicaciones ni analisis."""

r = requests.post(url, json={
    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    "generationConfig": {"temperature": 0.9, "maxOutputTokens": 1000}
}, timeout=120)

# Guardar respuesta completa
with open("_response.json", "w", encoding="utf-8") as f:
    json.dump(r.json(), f, ensure_ascii=False, indent=2)

data = r.json()
parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
for i, p in enumerate(parts):
    thought = p.get("thought", False)
    text = p.get("text", "N/A")
    with open("_response.txt", "a", encoding="utf-8") as f:
        f.write(f"=== Part {i} (thought={thought}) ===\n{text}\n\n")
    print(f"Part {i}: thought={thought}, len={len(text)}")

print("\nVer _response.txt para texto completo")
