"""
browser_manager.py — Gestor de Navegadores Playwright con Stealth
Lanza múltiples navegadores Chromium visibles, cada uno con:
- Proxy residencial español único
- User-Agent y fingerprint distintos
- Sesión persistente (cookies + storage)
- Plugin stealth anti-detección
"""
import asyncio
import random
import logging
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from playwright_stealth import stealth_async
from config import SESSIONS_DIR, MAX_CONCURRENT_BROWSERS

logger = logging.getLogger(__name__)

# ── Fingerprints: User-Agents reales de móviles Android/iOS España ────────
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.73 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SAMSUNG SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; OnePlus 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Redmi Note 13 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; V2250) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; 23028RNCAG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; CPH2585) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; M2007J20CG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; 2201116SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; 2107113SG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.90 Mobile/15E148 Safari/604.1",
]

# Resoluciones de pantalla para simular móviles reales
VIEWPORTS = [
    {"width": 412, "height": 915},   # Samsung Galaxy S21+
    {"width": 390, "height": 844},   # iPhone 14
    {"width": 393, "height": 873},   # Pixel 7
    {"width": 414, "height": 896},   # iPhone 11
    {"width": 360, "height": 800},   # Samsung Galaxy A54
    {"width": 428, "height": 926},   # iPhone 14 Pro Max
    {"width": 384, "height": 854},   # OnePlus 11
    {"width": 375, "height": 812},   # iPhone X
]


class GhostBrowser:
    """
    Wrapper de un navegador Playwright con stealth y proxy asignado.
    Cada instancia representa UNA cuenta de Instagram con SU proxy.
    """

    def __init__(self, account: dict, index: int):
        self.username = account["username"]
        self.password = account["password"]
        self.proxy_url = account.get("proxy", "")
        self.index = index
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None
        self._pw = None
        self._user_agent = USER_AGENTS[index % len(USER_AGENTS)]
        self._viewport = VIEWPORTS[index % len(VIEWPORTS)]

    @property
    def session_dir(self) -> Path:
        """Directorio de sesión persistente para esta cuenta."""
        d = SESSIONS_DIR / self.username
        d.mkdir(exist_ok=True)
        return d

    async def launch(self) -> Page:
        """Lanza el navegador visible con stealth + proxy."""
        self._pw = await async_playwright().start()

        launch_args = {
            "headless": False,  # ¡VISIBLE! El show del ratón fantasma
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--no-first-run",
                "--disable-extensions",
                f"--window-size={self._viewport['width'] + 50},{self._viewport['height'] + 100}",
                f"--window-position={80 * self.index},{60 * self.index}",
            ],
        }

        # Proxy residencial por cuenta
        if self.proxy_url:
            parts = self.proxy_url.replace("http://", "").split("@")
            if len(parts) == 2:
                user_pass = parts[0]
                host_port = parts[1]
                proxy_user, proxy_pass = user_pass.split(":", 1)
                launch_args["proxy"] = {
                    "server": f"http://{host_port}",
                    "username": proxy_user,
                    "password": proxy_pass,
                }
            else:
                launch_args["proxy"] = {"server": self.proxy_url}

        self.browser = await self._pw.chromium.launch(**launch_args)

        # Contexto con sesión persistente + fingerprint
        self.context = await self.browser.new_context(
            user_agent=self._user_agent,
            viewport=self._viewport,
            locale="es-ES",
            timezone_id="Europe/Madrid",
            geolocation={"latitude": 36.72 + random.uniform(-0.1, 0.1),
                         "longitude": -4.42 + random.uniform(-0.1, 0.1)},
            permissions=["geolocation"],
            color_scheme="light",
            storage_state=str(self.session_dir / "state.json") if (self.session_dir / "state.json").exists() else None,
        )

        self.page = await self.context.new_page()

        # Aplicar stealth anti-detección
        await stealth_async(self.page)

        logger.info(f"[Browser {self.index}] @{self.username} lanzado | proxy: {'✅' if self.proxy_url else '❌ SIN PROXY'}")
        return self.page

    async def save_session(self):
        """Guarda cookies y storage para no re-loguear."""
        if self.context:
            state = await self.context.storage_state()
            import json
            (self.session_dir / "state.json").write_text(
                json.dumps(state, indent=2, ensure_ascii=False)
            )
            logger.info(f"[Browser {self.index}] Sesión guardada para @{self.username}")

    async def close(self):
        """Cierra el navegador guardando sesión."""
        try:
            await self.save_session()
        except Exception as e:
            logger.warning(f"[Browser {self.index}] Error guardando sesión: {e}")
        if self.browser:
            await self.browser.close()
        if self._pw:
            await self._pw.stop()
        logger.info(f"[Browser {self.index}] Cerrado")

    async def screenshot(self, name: str = ""):
        """Captura de pantalla para debug/dashboard."""
        if self.page:
            path = self.session_dir / f"screenshot_{name or 'latest'}.png"
            await self.page.screenshot(path=str(path))
            return str(path)


class BrowserPool:
    """
    Pool de navegadores con semáforo de concurrencia.
    Controla cuántos se abren simultáneamente para no reventar la RAM.
    """

    def __init__(self, accounts: list[dict]):
        self.accounts = accounts
        self.browsers: dict[str, GhostBrowser] = {}
        self._semaphore = asyncio.Semaphore(MAX_CONCURRENT_BROWSERS)

    async def get_browser(self, username: str) -> GhostBrowser:
        """Obtiene o crea un navegador para una cuenta."""
        if username in self.browsers:
            return self.browsers[username]

        async with self._semaphore:
            acc = next((a for a in self.accounts if a["username"] == username), None)
            if not acc:
                raise ValueError(f"Cuenta {username} no encontrada en config")

            idx = self.accounts.index(acc)
            gb = GhostBrowser(acc, idx)
            await gb.launch()
            self.browsers[username] = gb
            return gb

    async def close_all(self):
        """Cierra todos los navegadores."""
        for gb in self.browsers.values():
            await gb.close()
        self.browsers.clear()

    def active_count(self) -> int:
        return len(self.browsers)
