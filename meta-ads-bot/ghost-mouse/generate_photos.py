"""
PHANTOM v3 — Generador de identidades ultra-realistas.
Nano Banana 2 con prompts profesionales: imperfecciones deliberadas.
"""
import requests
import base64
import os
import json
from config import GEMINI_KEY

NANO2_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-image-preview:generateContent?key={GEMINI_KEY}"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "phantom_identities")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Negative prompt profesional - anti-IA
NEG = """AVOID AT ALL COSTS: any sign of AI generation, perfect symmetry in face, overly smooth skin without pores or texture, plastic-looking skin, uncanny valley effect, perfect teeth alignment, eyes that are too bright or have catchlights that look artificial, hair that looks rendered or CG, ring light reflections, studio lighting setup, stock photography composition, Getty Images aesthetic, corporate headshot style, perfect bokeh circles, oversaturated colors, HDR tonemapping look, excessive sharpness, watermarks, text overlays, logos, extra fingers or deformed hands, anatomical errors, floating objects, inconsistent shadows, painted or illustrated look, depth of field that looks computed not optical, skin that looks airbrushed or FaceTuned, perfectly white teeth, perfectly symmetrical eyebrows"""

# Positive quality anchors
POS_BASE = """Shot on iPhone 14 Pro, natural HEIC compression artifacts, realistic lens distortion from wide front camera, authentic Instagram post aesthetic, real human with natural skin texture including visible pores and minor blemishes, slightly asymmetric facial features as real people have, natural teeth with realistic color variation, authentic hair with flyaway strands, genuine candid expression not posed"""

PROFILES = {
    "lauramtz.95": {
        "avatar": f"""Generate an ultra-photorealistic 1:1 square image.

POSITIVE: {POS_BASE}. Candid selfie of a Spanish woman aged 28, light brown wavy hair slightly frizzy from humidity, green-hazel eyes, natural skin with a small mole near her left eyebrow, no makeup or very minimal concealer only, wearing a worn-in oatmeal colored knit sweater with a small coffee stain barely visible on the sleeve, genuine surprised-happy smile like she just ran into a friend, sitting at a scratched wooden table in a small busy neighborhood cafe in Malaga, half-empty cortado coffee cup with lipstick mark on rim, her phone in a cracked screen case visible on table, window light creating natural shadows under her nose and chin, background showing real cafe patrons slightly out of focus, one person checking their phone, warm but not orange color temperature, slight lens flare from window, composition slightly off-center as if taken quickly

NEGATIVE: {NEG}""",

        "story": f"""Generate an ultra-photorealistic vertical 9:16 image.

POSITIVE: {POS_BASE}. Vertical candid photo of the same Spanish woman with wavy brown hair, late 20s, curled up on a worn grey IKEA couch in a small apartment, laptop balanced on knees showing a blurry Instagram insights screen, wearing an old oversized university hoodie and fuzzy socks, hair in a messy clip with strands falling out, no makeup showing under-eye circles from late work, warm yellow floor lamp as only light source creating strong shadows, coffee mug with old coffee rings on the side table next to used tissues and a half-eaten cookie, phone charger cable running across frame, slightly grainy low-light phone photo taken from the doorway, focus slightly soft as if shot through glass, real lived-in apartment with mismatched cushions and a blanket thrown over the couch arm

NEGATIVE: {NEG}""",
    },
    "carlosruiz.88": {
        "avatar": f"""Generate an ultra-photorealistic 1:1 square image.

POSITIVE: {POS_BASE}. Outdoor terrace selfie of a Spanish man aged 34, short dark brown hair with a few grey strands at temples showing naturally, 4-day stubble with patchy spot on right cheek, slight sunburn on nose and forehead from being outdoors, brown eyes with natural bloodshot from a long day, wearing a faded washed-out navy polo shirt with collar slightly uneven, one side tucked behind ear of his sunglasses resting on head, wide genuine grin showing slightly crooked bottom teeth, sitting at a metal bistro table at a tapas bar in Madrid Salamanca district, half-drunk cerveza in a dewy glass next to a small plate of aceitunas, his arm extended holding phone showing slight motion blur on fingers, golden hour sunlight creating warm tone on left side of face while right side is in shadow, background showing blurred Madrid architecture and other diners, frame slightly tilted 3 degrees as selfies often are

NEGATIVE: {NEG}""",

        "story": f"""Generate an ultra-photorealistic vertical 9:16 image.

POSITIVE: {POS_BASE}. Vertical candid photo of Spanish man mid-30s with stubble, shot from behind-side angle by someone in the doorway, sitting at a cluttered IKEA Malm desk with 27-inch monitor showing a Notion page with task lists, second smaller laptop open to the side showing WhatsApp Web, wearing a wrinkled plain dark grey t-shirt, barefoot visible under desk, desk has scattered items: empty water bottle, wireless mouse on a worn mousepad, sticky notes on monitor edge, cable management disaster visible, blue-white screen glow on his face mixed with warm desk lamp, nighttime visible through window with city lights, he is rubbing his eyes with one hand showing fatigue, slightly soft focus typical of phone photo in low light, slight noise grain from ISO being too high

NEGATIVE: {NEG}""",
    },
    "anabelenn.90": {
        "avatar": f"""Generate an ultra-photorealistic 1:1 square image.

POSITIVE: {POS_BASE}. Bathroom mirror selfie of a real Spanish woman aged 30, dark brown curly hair still slightly damp from shower, wearing a simple white ribbed tank top, gold small hoop earrings and a thin chain necklace, natural face with visible small acne scar on chin and slight dark circles, mascara just applied with a tiny smudge on upper lid she hasn't noticed, warm bathroom vanity light from above creating slight shadow under chin, phone in a rose gold case held at chest height, mirror has slight water drops and toothpaste spatter near the edge, background showing real bathroom: towel rack with mismatched towels, shower curtain partially visible, toiletries clustered on shelf, her expression is a natural half-smile like she's checking how she looks before going out, composition centered but phone covers part of her chest naturally

NEGATIVE: {NEG}""",

        "story": f"""Generate an ultra-photorealistic vertical 9:16 image.

POSITIVE: {POS_BASE}. Vertical photo of a Spanish woman with dark curly hair aged 30, at a tapas restaurant terrace in Marbella at sunset, she is standing and leaning over a table to take a photo of food with her phone, shot from side by her friend sitting at the table, wearing a casual striped Zara summer dress, her bag hanging on chair, table has authentic Spanish dishes: tortilla, croquetas, a tintos de verano with condensation, paper napkins and bread basket, she is concentrating with tongue slightly visible biting lip, her hair falling forward, golden sunset light from behind creating a slight silhouette and lens flare, Mediterranean white buildings and palm tree visible in background, other real-looking diners at next table, one checking phone, warm color palette but not oversaturated, slight chromatic aberration at frame edges from phone lens

NEGATIVE: {NEG}""",
    },
    "pablofdezz86": {
        "avatar": f"""Generate an ultra-photorealistic 1:1 square image.

POSITIVE: {POS_BASE}. Park bench selfie of a real Spanish man aged 30, dark messy hair that needs a cut with one side sticking up from wind, clean shaven with visible razor bump on neck, wearing a plain faded black crew neck t-shirt with slight pilling, wired earbuds hanging around neck with one earbud dangling, holding phone to take selfie with his free hand while other hand holds a takeaway coffee cup with sleeve, relaxed smirk not a full smile, sitting on a weathered wooden park bench in Retiro Park Madrid, dappled tree shadow on his face creating natural light patches, background showing blurred joggers and dog walker on path, fallen leaves on ground, his backpack strap visible on one shoulder, slightly warm afternoon light, composition off-center with more space on left side, visible slight thumb edge at bottom corner of frame as if almost covering lens

NEGATIVE: {NEG}""",

        "story": f"""Generate an ultra-photorealistic vertical 9:16 image.

POSITIVE: {POS_BASE}. Vertical candid photo of young Spanish man aged 30 working on silver MacBook Pro at a beach chiringuito in Malaga coast, shot by a friend from across the small wooden table, wearing a wrinkled cream linen shirt with sleeves rolled up showing tanned forearms and a simple leather bracelet, cheap plastic sunglasses pushed up on head, iced cafe con leche in a tall glass with melting ice next to laptop, sandy flip flops visible under table with sand on feet, background showing out-of-focus Mediterranean sea with actual people swimming, straw parasol edge visible at top of frame, laptop screen showing spreadsheet but glare makes it hard to read, real beach bar setting with plastic chairs, warm sunny natural light with harsh shadows typical of direct Spanish sun, slight sweat visible on forehead

NEGATIVE: {NEG}""",
    },
    "martadiaz.24": {
        "avatar": f"""Generate an ultra-photorealistic 1:1 square image.

POSITIVE: {POS_BASE}. Rooftop selfie of a real young Spanish woman aged 27, straight dark brown hair in a hasty low ponytail with baby hairs framing forehead, minimal makeup just lip balm, genuine laughing expression with nose scrunched up and eyes almost closing showing natural crow's feet, wearing a simple white v-neck Primark t-shirt with phone tan line visible on forearm, on a residential rooftop terrace in Seville with hanging laundry visible in background and potted plants, windy day with hair wisps blowing across face, blue sky with actual clouds not perfect gradient, strong afternoon sun creating sharp shadow on one side of face, she is squinting slightly from the sun, her fingers visible at bottom edge holding phone, frame slightly tilted, natural cheerful spontaneous energy, not posed

NEGATIVE: {NEG}""",

        "story": f"""Generate an ultra-photorealistic vertical 9:16 image.

POSITIVE: {POS_BASE}. Vertical photo of young Spanish woman aged 27 with dark hair in ponytail, sitting cross-legged on a worn wooden floor in her small studio apartment, laptop open in front of her showing Canva design, scattered around her: notebook with handwritten notes and doodles, colorful sticky notes on the white wall behind her forming a rough mind map with real handwriting, her phone face-down next to her, wearing old grey joggers and an oversized band t-shirt, string fairy lights on the wall above providing warm yellow glow, it's evening, take-away sushi container half-eaten next to her, she is biting a pen cap while thinking and looking at the wall not camera, shot from standing position above by a roommate, real studio apartment with visible electrical cables and a small bookshelf with actual book spines, lived-in authentic creative workspace

NEGATIVE: {NEG}""",
    },
}


def generate_image(prompt, filename):
    """Generar imagen con Nano Banana 2."""
    try:
        r = requests.post(NANO2_URL, json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["image", "text"]}
        }, timeout=120)
        data = r.json()

        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if "inlineData" in part:
                    img_data = base64.b64decode(part["inlineData"]["data"])
                    filepath = os.path.join(OUTPUT_DIR, filename)
                    with open(filepath, "wb") as f:
                        f.write(img_data)
                    size = len(img_data) // 1024
                    print(f"  OK {filename} ({size}KB)")
                    return filepath

        reason = ""
        if data.get("candidates"):
            reason = data["candidates"][0].get("finishReason", "")
        print(f"  FAIL {filename} ({reason})")
        return None

    except Exception as e:
        print(f"  ERR {filename}: {str(e)[:60]}")
        return None


if __name__ == "__main__":
    print("=" * 55)
    print("  PHANTOM — IDENTIDADES ULTRA-REALISTAS v3")
    print("  Nano Banana 2 + Prompts Profesionales")
    print("=" * 55)

    for username, data in PROFILES.items():
        print(f"\n[@{username}]")
        generate_image(data["avatar"], f"{username}_avatar.png")
        generate_image(data["story"], f"{username}_story.png")

    print(f"\n{'='*55}")
    print(f"Fotos en: {OUTPUT_DIR}")
    print(f"{'='*55}")
