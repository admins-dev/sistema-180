"""
ig_automator.py — Automatización Visual de Instagram
Controla la interfaz web de Instagram como si fuera un humano real.
Login, navegación, scraping de perfiles, envío de DMs — todo visual.
"""
import asyncio
import random
import logging
from human_cursor import human_click_element, human_type, human_scroll, move_mouse
from browser_manager import GhostBrowser

logger = logging.getLogger(__name__)

IG_BASE = "https://www.instagram.com"


async def _wait_random(min_s: float = 1.0, max_s: float = 3.0):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def ig_login(ghost: GhostBrowser) -> bool:
    """
    Login visual en Instagram.
    Si hay sesión guardada, verifica que sigue activa.
    Si no, hace login manual con cursor humano.
    """
    page = ghost.page
    if not page:
        return False

    # Navegar a Instagram
    await page.goto(f"{IG_BASE}/", wait_until="domcontentloaded")
    await _wait_random(2, 4)

    # Aceptar cookies si aparece el banner
    try:
        cookie_btn = page.locator("button:has-text('Permitir'), button:has-text('Allow'), button:has-text('Aceptar')")
        if await cookie_btn.count() > 0:
            await human_click_element(page, "button:has-text('Permitir'), button:has-text('Allow'), button:has-text('Aceptar')")
            await _wait_random(1, 2)
    except Exception:
        pass

    # Verificar si ya estamos logueados (sesión persistente)
    try:
        # Si vemos el icono de home/perfil, estamos dentro
        home_icon = page.locator('a[href="/"]').first
        if await home_icon.is_visible(timeout=3000):
            logger.info(f"[@{ghost.username}] Sesión activa detectada ✅")
            return True
    except Exception:
        pass

    # Login manual
    logger.info(f"[@{ghost.username}] Haciendo login visual...")
    try:
        await page.goto(f"{IG_BASE}/accounts/login/", wait_until="domcontentloaded")
        await _wait_random(2, 4)

        # Rellenar usuario
        username_input = page.locator('input[name="username"]')
        await human_click_element(page, 'input[name="username"]')
        await _wait_random(0.3, 0.8)
        await human_type(page, ghost.username)
        await _wait_random(0.5, 1.2)

        # Rellenar contraseña
        await human_click_element(page, 'input[name="password"]')
        await _wait_random(0.3, 0.6)
        await human_type(page, ghost.password)
        await _wait_random(0.8, 1.5)

        # Click en "Iniciar sesión"
        login_btn = page.locator('button[type="submit"]')
        await human_click_element(page, 'button[type="submit"]')
        await _wait_random(4, 7)

        # Manejar "Guardar información de inicio de sesión"
        try:
            save_btn = page.locator("button:has-text('Guardar'), button:has-text('Save')")
            if await save_btn.count() > 0:
                await human_click_element(page, "button:has-text('Guardar'), button:has-text('Save')")
                await _wait_random(2, 3)
        except Exception:
            pass

        # Manejar "Activar notificaciones" → Ahora no
        try:
            not_now = page.locator("button:has-text('Ahora no'), button:has-text('Not Now')")
            if await not_now.count() > 0:
                await human_click_element(page, "button:has-text('Ahora no'), button:has-text('Not Now')")
                await _wait_random(1, 2)
        except Exception:
            pass

        # Guardar sesión
        await ghost.save_session()
        logger.info(f"[@{ghost.username}] Login exitoso ✅")
        return True

    except Exception as e:
        logger.error(f"[@{ghost.username}] Login fallido: {e}")
        return False


async def scrape_profile(ghost: GhostBrowser, target_username: str) -> dict | None:
    """
    Navega al perfil de un usuario y extrae su info visible.
    Retorna dict con nombre, bio, seguidores, o None si falla.
    """
    page = ghost.page
    if not page:
        return None

    try:
        await page.goto(f"{IG_BASE}/{target_username}/", wait_until="domcontentloaded")
        await _wait_random(2, 4)

        # Simular lectura humana: scroll suave
        await human_scroll(page, "down", random.randint(100, 250))
        await _wait_random(1, 3)

        # Extraer datos del perfil
        profile_data = await page.evaluate("""() => {
            const nameEl = document.querySelector('header section span, header h1, header h2');
            const bioEl = document.querySelector('header section > div > span, header section div.-vDIg span');
            const statsEls = document.querySelectorAll('header section ul li span span, header section ul li button span span');
            
            let followers = 0;
            let following = 0;
            let posts = 0;
            
            statsEls.forEach((el, i) => {
                const text = el.textContent || el.title || '';
                const num = parseInt(text.replace(/[.,\s]/g, '')) || 0;
                if (i === 0) posts = num;
                if (i === 1) followers = num;
                if (i === 2) following = num;
            });
            
            // Intento alternativo para bio
            let bio = '';
            const bioContainer = document.querySelector('header section > div');
            if (bioContainer) {
                const spans = bioContainer.querySelectorAll('span');
                spans.forEach(s => {
                    if (s.textContent && s.textContent.length > 10 && s.textContent.length < 300) {
                        bio = s.textContent;
                    }
                });
            }
            
            return {
                name: nameEl ? nameEl.textContent.trim() : '',
                bio: bio,
                followers: followers,
                following: following,
                posts: posts,
            };
        }""")

        if profile_data:
            profile_data["username"] = target_username
            logger.info(
                f"[@{ghost.username}] Perfil escaneado: @{target_username} | "
                f"{profile_data.get('followers', 0)} seguidores"
            )
            return profile_data

    except Exception as e:
        logger.error(f"[@{ghost.username}] Error scraping @{target_username}: {e}")

    return None


async def send_dm(ghost: GhostBrowser, target_username: str, message: str) -> bool:
    """
    Envía un DM a un usuario de Instagram de forma visual.
    Navega a su perfil → click en "Mensaje" → escribe → envía.
    """
    page = ghost.page
    if not page:
        return False

    try:
        # Navegar al perfil del target
        await page.goto(f"{IG_BASE}/{target_username}/", wait_until="domcontentloaded")
        await _wait_random(2, 4)

        # Simular que miramos el perfil (pausa de lectura)
        await human_scroll(page, "down", random.randint(50, 200))
        await _wait_random(1.5, 4)

        # Click en "Mensaje" / "Message"
        msg_btn = page.locator("div[role='button']:has-text('Mensaje'), div[role='button']:has-text('Message'), button:has-text('Mensaje'), button:has-text('Message')")
        if await msg_btn.count() == 0:
            # Intentar con el botón alternativo
            msg_btn = page.locator("[data-testid='message-button'], a[href*='/direct/t/']")

        if await msg_btn.count() == 0:
            logger.warning(f"[@{ghost.username}] No se encuentra botón 'Mensaje' en @{target_username}")
            return False

        await human_click_element(page, msg_btn.first)
        await _wait_random(2, 4)

        # Manejar popup de "Activar notificaciones" si aparece
        try:
            not_now = page.locator("button:has-text('Ahora no'), button:has-text('Not Now')")
            if await not_now.count() > 0:
                await human_click_element(page, not_now.first)
                await _wait_random(1, 2)
        except Exception:
            pass

        # Localizar el campo de texto del chat
        text_area = page.locator(
            "textarea[placeholder*='Mensaje'], "
            "textarea[placeholder*='Message'], "
            "div[role='textbox'][contenteditable='true'], "
            "textarea[aria-label*='Mensaje']"
        )

        if await text_area.count() == 0:
            logger.warning(f"[@{ghost.username}] No se encuentra campo de texto DM")
            return False

        # Hacer click en el campo de texto
        await human_click_element(page, text_area.first)
        await _wait_random(0.5, 1.0)

        # Teclear el mensaje con delays humanos
        await human_type(page, message)
        await _wait_random(0.8, 2.0)

        # Enviar con Enter (o click en botón enviar)
        await page.keyboard.press("Enter")
        await _wait_random(1.5, 3.0)

        # Guardar sesión actualizada
        await ghost.save_session()

        logger.info(f"[@{ghost.username}] ✅ DM enviado a @{target_username}")
        return True

    except Exception as e:
        logger.error(f"[@{ghost.username}] ❌ Error enviando DM a @{target_username}: {e}")
        return False


async def search_hashtag_targets(ghost: GhostBrowser, hashtag: str, limit: int = 10) -> list[str]:
    """
    Busca usuarios de Instagram a través de un hashtag.
    Navega a la página del hashtag y extrae usernames de los posts recientes.
    """
    page = ghost.page
    if not page:
        return []

    usernames = []
    try:
        await page.goto(f"{IG_BASE}/explore/tags/{hashtag}/", wait_until="domcontentloaded")
        await _wait_random(3, 5)

        # Scroll para cargar más posts
        for _ in range(3):
            await human_scroll(page, "down", random.randint(300, 600))
            await _wait_random(1.5, 3)

        # Extraer links a posts y luego a perfiles
        post_links = await page.evaluate("""() => {
            const links = document.querySelectorAll('a[href*="/p/"]');
            return Array.from(links).slice(0, 30).map(a => a.href);
        }""")

        for link in post_links[:limit * 2]:
            if len(usernames) >= limit:
                break
            try:
                await page.goto(link, wait_until="domcontentloaded")
                await _wait_random(1.5, 3)

                # Extraer username del post
                username = await page.evaluate("""() => {
                    const link = document.querySelector('header a[href*="/"]');
                    if (link) {
                        const href = link.getAttribute('href') || '';
                        return href.replace(/\\//g, '');
                    }
                    return '';
                }""")

                if username and username not in usernames:
                    usernames.append(username)
                    logger.info(f"[#{hashtag}] Target encontrado: @{username}")
            except Exception:
                continue

    except Exception as e:
        logger.error(f"Error buscando #{hashtag}: {e}")

    return usernames
