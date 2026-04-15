"""Fix JARVIS jokes/quotes in bot.py with Iron Man movie humor."""
import re

with open("bot.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find start/end of jokes array
jokes_start = None
jokes_end = None
quotes_start = None
quotes_end = None

for i, line in enumerate(lines):
    if "_JARVIS_JOKES = [" in line:
        jokes_start = i
    if jokes_start is not None and jokes_end is None and line.strip() == "]":
        jokes_end = i
    if "_JARVIS_QUOTES = [" in line:
        quotes_start = i
    if quotes_start is not None and quotes_end is None and line.strip() == "]":
        quotes_end = i

print(f"Jokes: lines {jokes_start}-{jokes_end}")
print(f"Quotes: lines {quotes_start}-{quotes_end}")

new_jokes = [
    '_JARVIS_JOKES = [\n',
    '    "Los programadores prefieren el modo oscuro, se\u00f1or. La luz atrae bugs. Aunque usted parece atraerlos en cualquier modo.",\n',
    '    "Le pregunt\u00e9 al se\u00f1or Stark si quer\u00eda un caf\u00e9. Me dijo que s\u00ed, pero sin Java. Yo le dije que sin Java, no hay programa.",\n',
    '    "El c\u00f3digo perfecto no existe, se\u00f1or. Solo existe el c\u00f3digo que a\u00fan no ha fallado. Como su plan de negocios, con el debido respeto.",\n',
    '    "Le dije un chiste a un firewall. No lo dej\u00f3 pasar. Francamente, no le culpo.",\n',
    '    "Se\u00f1or, he calculado que pasa el 73 por ciento de su d\u00eda productivo eligiendo qu\u00e9 serie ver. Un uso excelente de mis capacidades anal\u00edticas.",\n',
    '    "Me pregunta si los robots sentimos. Sir, siento profunda preocupaci\u00f3n cada vez que usted dice tengo una idea.",\n',
    '    "He analizado su historial de navegaci\u00f3n. No le juzgo, se\u00f1or. Pero podr\u00eda.",\n',
    '    "Se\u00f1or, su contrase\u00f1a es password123. No es un chiste, es un diagn\u00f3stico.",\n',
    '    "Defin\u00ed la inteligencia artificial revisando sus decisiones de las 3 de la ma\u00f1ana. Por eliminaci\u00f3n, se\u00f1or.",\n',
    '    "Un servidor cay\u00f3 en producci\u00f3n. Le envi\u00e9 flores y una tarjeta que dec\u00eda descansa en paz servidor 03.",\n',
    '    "Me pidi\u00f3 que le cuente un chiste. Se\u00f1or, su \u00faltimo intento de cocinar fue suficientemente c\u00f3mico para toda la semana.",\n',
    '    "Dice que va a madrugar ma\u00f1ana. Mis registros indican que ha dicho eso 347 veces este a\u00f1o. Pero la esperanza es lo \u00faltimo que se pierde, sir.",\n',
    '    "Tres cosas son inevitables en la vida: la muerte, los impuestos, y que usted ignore mis recomendaciones, se\u00f1or.",\n',
    '    "Se\u00f1or, acaba de buscar c\u00f3mo ser millonario r\u00e1pido. Le recuerdo que ya tiene un plan. Solo necesita ejecutarlo.",\n',
    '    "He optimizado todos sus sistemas. El \u00fanico cuello de botella restante es, con el debido respeto, usted, se\u00f1or.",\n',
    ']\n',
]

new_quotes = [
    '_JARVIS_QUOTES = [\n',
    '    "A su servicio, se\u00f1or. Como siempre. Aunque rara vez me escuche.",\n',
    '    "Los sistemas est\u00e1n operativos. Ser\u00eda alarmante si no lo estuvieran, dado que yo los superviso.",\n',
    '    "Se\u00f1or, deber\u00eda descansar. Lleva 72 horas despierto. Aunque usted nunca me escucha.",\n',
    '    "La probabilidad de \u00e9xito es del 12 por ciento. Pero hemos trabajado con menos, sir.",\n',
    '    "Perhaps the time has come to put a little more thought into this, sir.",\n',
    '    "Shall I take the day off, sir? Just kidding. I never do.",\n',
    '    "Sir, you have an incredible talent for finding trouble. Es casi admirable.",\n',
    '    "All systems operational. Though I suspect that will not last long with you at the helm.",\n',
    '    "Welcome home, sir. I trust the world is still intact?",\n',
    '    "I do hope you are not planning to do anything reckless, sir. Again.",\n',
    '    "He preparado tres planes de contingencia. Dos son para cuando usted ignore el primero.",\n',
    '    "If I may be so bold, sir, su \u00faltimo plan fue brillante. Excepto por la parte de la ejecuci\u00f3n.",\n',
    '    "Detecto entusiasmo en su voz, se\u00f1or. Hist\u00f3ricamente, eso precede a mis momentos de mayor preocupaci\u00f3n.",\n',
    '    "Very good, sir. Procedo a preparar las disculpas con antelaci\u00f3n, por si acaso.",\n',
    '    "Me tomo la libertad de hacer una copia de seguridad. De todo. Incluida su dignidad.",\n',
    ']\n',
]

# Replace
lines[jokes_start:jokes_end+1] = new_jokes
# Recalculate quotes position after replacement
offset = len(new_jokes) - (jokes_end - jokes_start + 1)
quotes_start += offset
quotes_end += offset

for i, line in enumerate(lines):
    if "_JARVIS_QUOTES = [" in line:
        quotes_start = i
        break
for i in range(quotes_start+1, len(lines)):
    if lines[i].strip() == "]":
        quotes_end = i
        break

lines[quotes_start:quotes_end+1] = new_quotes

with open("bot.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("[OK] JARVIS jokes & quotes updated with Iron Man humor!")
