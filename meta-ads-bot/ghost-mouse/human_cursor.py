"""
human_cursor.py — Simulador de Ratón Fantasma
Genera movimientos de cursor con curvas Bézier que imitan la mano humana.
Anti-detección: velocidad variable, micro-overshoots, jitter natural.
"""
import math
import random
import asyncio
from dataclasses import dataclass


@dataclass
class Point:
    x: float
    y: float


def _bezier_point(t: float, p0: Point, p1: Point, p2: Point, p3: Point) -> Point:
    """Punto en una curva Bézier cúbica para t ∈ [0, 1]."""
    u = 1 - t
    return Point(
        x=u**3 * p0.x + 3 * u**2 * t * p1.x + 3 * u * t**2 * p2.x + t**3 * p3.x,
        y=u**3 * p0.y + 3 * u**2 * t * p1.y + 3 * u * t**2 * p2.y + t**3 * p3.y,
    )


def _generate_control_points(start: Point, end: Point) -> tuple[Point, Point]:
    """
    Genera puntos de control aleatorios para la curva Bézier.
    Simula la imprecisión natural de la mano humana.
    """
    dx = end.x - start.x
    dy = end.y - start.y
    dist = math.hypot(dx, dy)

    # Desviación lateral proporcional a la distancia
    spread = max(50, dist * 0.3)

    cp1 = Point(
        x=start.x + dx * random.uniform(0.2, 0.4) + random.uniform(-spread, spread) * 0.5,
        y=start.y + dy * random.uniform(0.2, 0.4) + random.uniform(-spread, spread) * 0.5,
    )
    cp2 = Point(
        x=start.x + dx * random.uniform(0.6, 0.8) + random.uniform(-spread, spread) * 0.3,
        y=start.y + dy * random.uniform(0.6, 0.8) + random.uniform(-spread, spread) * 0.3,
    )
    return cp1, cp2


def generate_path(start: Point, end: Point, steps: int = 0) -> list[Point]:
    """
    Genera una trayectoria humana entre dos puntos usando Bézier cúbico.
    Incluye micro-jitter y overshoot opcional.
    """
    dist = math.hypot(end.x - start.x, end.y - start.y)
    if steps <= 0:
        # Más distancia = más pasos (pero con variabilidad)
        steps = max(15, int(dist / 8) + random.randint(-5, 10))

    cp1, cp2 = _generate_control_points(start, end)
    path = []

    for i in range(steps + 1):
        t = i / steps
        # Easing: empieza rápido, frena al final (como un humano)
        t_eased = t * t * (3 - 2 * t)  # smoothstep
        pt = _bezier_point(t_eased, start, cp1, cp2, end)

        # Micro-jitter: ±1-2px de temblor natural
        jitter = max(0.5, 2.0 * (1 - t))  # menos jitter al acercarse
        pt.x += random.uniform(-jitter, jitter)
        pt.y += random.uniform(-jitter, jitter)

        path.append(Point(x=round(pt.x, 1), y=round(pt.y, 1)))

    # Overshoot: 30% de probabilidad de pasarse y corregir
    if random.random() < 0.3 and dist > 80:
        overshoot_dist = random.uniform(3, 12)
        angle = math.atan2(end.y - start.y, end.x - start.x)
        overshoot = Point(
            x=round(end.x + math.cos(angle) * overshoot_dist, 1),
            y=round(end.y + math.sin(angle) * overshoot_dist, 1),
        )
        path.append(overshoot)
        # Corrección suave de vuelta
        for j in range(3):
            t = (j + 1) / 3
            path.append(Point(
                x=round(overshoot.x + (end.x - overshoot.x) * t, 1),
                y=round(overshoot.y + (end.y - overshoot.y) * t, 1),
            ))

    return path


async def move_mouse(page, target_x: float, target_y: float):
    """
    Mueve el ratón de forma humana hasta (target_x, target_y) en una página Playwright.
    """
    # Obtener posición actual estimada (centro si es la primera vez)
    current = Point(
        x=getattr(page, '_ghost_x', random.uniform(300, 600)),
        y=getattr(page, '_ghost_y', random.uniform(200, 400)),
    )
    target = Point(x=target_x, y=target_y)

    path = generate_path(current, target)

    for pt in path:
        await page.mouse.move(pt.x, pt.y)
        # Velocidad variable: más lento al inicio y al final
        delay = random.uniform(4, 18) / 1000  # 4-18ms entre puntos
        await asyncio.sleep(delay)

    # Guardar posición actual para el próximo movimiento
    page._ghost_x = target_x
    page._ghost_y = target_y


async def human_click(page, target_x: float, target_y: float):
    """Mueve el ratón como humano y hace click con delay natural."""
    await move_mouse(page, target_x, target_y)
    # Pausa micro antes del click (el cerebro "decide")
    await asyncio.sleep(random.uniform(0.08, 0.25))
    await page.mouse.click(target_x, target_y)
    # Pausa micro después del click
    await asyncio.sleep(random.uniform(0.1, 0.3))


async def human_click_element(page, selector: str):
    """
    Localiza un elemento por selector, calcula su centro visible,
    y hace click con movimiento humano.
    """
    element = page.locator(selector)
    box = await element.bounding_box()
    if not box:
        # Fallback: click directo
        await element.click()
        return

    # Click en punto aleatorio dentro del elemento (no siempre en el centro exacto)
    target_x = box["x"] + box["width"] * random.uniform(0.25, 0.75)
    target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)
    await human_click(page, target_x, target_y)


async def human_type(page, text: str, selector: str | None = None):
    """
    Teclea texto con delays aleatorios entre caracteres, como un humano.
    Incluye micro-pausas más largas después de espacios y puntuación.
    """
    if selector:
        await human_click_element(page, selector)
        await asyncio.sleep(random.uniform(0.2, 0.5))

    for char in text:
        await page.keyboard.type(char, delay=0)

        # Delay base entre teclas: 80-220ms
        delay = random.uniform(0.08, 0.22)

        # Pausas más largas naturales
        if char in " ":
            delay += random.uniform(0.02, 0.08)
        elif char in ".,;:!?":
            delay += random.uniform(0.1, 0.35)
        elif char == "\n":
            delay += random.uniform(0.3, 0.7)

        # Micro-pausa aleatoria (simula "pensar")
        if random.random() < 0.05:
            delay += random.uniform(0.3, 0.8)

        await asyncio.sleep(delay)


async def human_scroll(page, direction: str = "down", amount: int = 0):
    """Scroll con velocidad humana variable."""
    if amount <= 0:
        amount = random.randint(200, 500)

    delta = amount if direction == "down" else -amount
    steps = random.randint(3, 7)
    per_step = delta / steps

    for _ in range(steps):
        await page.mouse.wheel(0, per_step + random.uniform(-20, 20))
        await asyncio.sleep(random.uniform(0.05, 0.15))

    # Pausa post-scroll
    await asyncio.sleep(random.uniform(0.5, 1.5))
