"""
Ghost Mouse — DM Sender v6 DEFINITIVO.
Flujo probado: inbox -> compose -> busca -> clic primera fila -> Chat -> escribe -> Enter.
"""
import time
import random
import os

SHOTS = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SHOTS, exist_ok=True)


def send_dm(page, target_instagram, message):
    username = target_instagram.lstrip("@")

    try:
        # 1 - Inbox
        page.goto("https://www.instagram.com/direct/inbox/", wait_until="domcontentloaded")
        time.sleep(2)
        for txt in ["Ahora no", "Not Now"]:
            try: page.click(f'text="{txt}"', timeout=800)
            except: pass

        # 2 - Clic compose
        try:
            page.click('svg[aria-label="Nuevo mensaje"]', timeout=3000)
        except:
            try: page.click('svg[aria-label="New message"]', timeout=2000)
            except:
                try: page.click('text="Enviar mensaje"', timeout=2000)
                except: return False, "NO_COMPOSE"
        time.sleep(1.5)

        # 3 - Buscar usuario
        search = page.locator('input[name="queryBox"]')
        if search.count() == 0:
            search = page.locator('input[placeholder*="Busca"]')
        if search.count() == 0:
            return False, "NO_SEARCH"

        search.first.click()
        search.first.fill(username)
        time.sleep(2.5)

        # 4 - CLICAR PRIMERA FILA de resultados
        # Los resultados son divs dentro del dialog, debajo del input
        # Cada fila tiene un circulo de avatar + texto. Buscamos el primer div clickeable
        clicked = False

        # Metodo 1: buscar texto exacto del username
        try:
            result = page.locator(f'div[role="dialog"] >> text="{username}"').first
            result.click(timeout=3000)
            clicked = True
        except:
            pass

        # Metodo 2: Buscar checkbox o radio
        if not clicked:
            try:
                checkbox = page.locator('div[role="dialog"] input[type="checkbox"], div[role="dialog"] input[type="radio"]').first
                checkbox.click(timeout=2000)
                clicked = True
            except:
                pass

        # Metodo 3: Clicar en el primer div con imagen (avatar) en resultados
        if not clicked:
            try:
                # Buscar primer div con img (avatar del usuario)
                avatar_row = page.locator('div[role="dialog"] img[alt]').first
                avatar_row.click(timeout=2000)
                clicked = True
            except:
                pass

        # Metodo 4: JavaScript - clicar primer resultado
        if not clicked:
            try:
                page.evaluate("""() => {
                    const dialog = document.querySelector('div[role="dialog"]');
                    if (!dialog) return;
                    const items = dialog.querySelectorAll('div[style*="cursor"]');
                    if (items.length > 0) items[0].click();
                }""")
                clicked = True
            except:
                pass

        if not clicked:
            page.screenshot(path=os.path.join(SHOTS, f"dm_noclick_{username}.png"))
            return False, "CANT_SELECT_USER"

        time.sleep(1)
        page.screenshot(path=os.path.join(SHOTS, f"dm_selected_{username}.png"))

        # 5 - Clic "Chat"
        try:
            page.click('div[role="button"]:has-text("Chat")', timeout=5000)
        except:
            try: page.click('button:has-text("Chat")', timeout=3000)
            except:
                try: page.click('div[role="button"]:has-text("Siguiente")', timeout=3000)
                except: return False, "NO_CHAT_BTN"
        
        time.sleep(2)

        # 6 - Textarea con retry
        textarea = None
        for _ in range(5):
            for sel in [
                'div[role="textbox"][contenteditable="true"]',
                'div[contenteditable="true"]',
                'div[role="textbox"]',
                'textarea',
            ]:
                el = page.locator(sel)
                if el.count() > 0:
                    textarea = el.first
                    break
            if textarea: break
            time.sleep(1)

        if textarea is None:
            page.screenshot(path=os.path.join(SHOTS, f"dm_notext_{username}.png"))
            return False, "NO_TEXTAREA"

        textarea.click()
        time.sleep(0.2)

        # 7 - Escribir
        for char in message:
            page.keyboard.type(char, delay=random.randint(10, 30))
        time.sleep(0.3)

        # 8 - Enter
        page.keyboard.press("Enter")
        time.sleep(1)

        print(f"    DM ENVIADO a @{username}!")
        return True, "SENT"

    except Exception as e:
        print(f"    Error: {str(e)[:100]}")
        return False, f"ERROR: {str(e)[:50]}"
