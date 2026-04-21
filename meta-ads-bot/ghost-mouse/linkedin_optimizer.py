"""
LinkedIn Profile Optimizer — Ghost Mouse
Actualiza el perfil de LinkedIn con movimientos humanos Bézier.
"""
import asyncio
import random
import time
import os
from playwright.async_api import async_playwright
from human_cursor import move_mouse, human_click, human_type, human_scroll

PROFILES_DIR = os.path.join(os.path.dirname(__file__), "profiles")
LINKEDIN_PROFILE_DIR = os.path.join(PROFILES_DIR, "linkedin_main")
os.makedirs(LINKEDIN_PROFILE_DIR, exist_ok=True)

PROFILE_URL = "https://www.linkedin.com/in/jos%C3%A9-mar%C3%ADa-moreno-91b5922a5/"

# ===================================================================
# CONTENIDO OPTIMIZADO B7 + MONGEMALO
# ===================================================================

NEW_HEADLINE = "Monto sistemas de captación con IA para negocios que facturan pero no escalan | 57 agentes IA | Fundador de Sistema 180"

NEW_ABOUT = """Si facturas pero no escalas, sigue leyendo. Si no, pasa de largo.

Soy José María Moreno. Fundador de Sistema 180.

Monto sistemas de captación automatizados para infoproductores y negocios locales que hacen bien su trabajo pero dependen del boca a boca y del algoritmo para conseguir clientes.

El problema es simple: publicas contenido, tienes seguidores, tu servicio es bueno. Pero los DMs de compra no llegan. Y cada mes cierras con la misma facturación que hace 6 meses.

La solución también es simple: un sistema que convierte tráfico en conversaciones de venta. Sin funnels de 7 pasos. Sin VSLs de 45 minutos. Sin landing pages de 3.000 palabras.

Mi sistema funciona así:
→ Contenido que atrae al cliente correcto
→ Ads que amplifican lo que ya funciona
→ Perfil que convierte visitantes en interesados
→ Bot que filtra y cualifica automáticamente
→ Cierre humano (tú o tu setter)

Detrás de esto hay 57 agentes de IA que trabajan 24/7: generan guiones, editan vídeos, publican contenido, prospectan por email/LinkedIn/Instagram, y gestionan el CRM completo.

Resultados:
✓ 12 clientes nuevos/mes para negocios locales desde la web
✓ Sistemas montados en 5-21 días
✓ ROI medio del 400% sobre inversión

No trabajo con todo el mundo. Solo con:
• Negocios locales que quieren aparecer en Google (desde 497€)
• Infoproductores que facturan +5k/mes y quieren escalar

Si eres uno de los dos, escríbeme. Si no, sígueme — el contenido que publico te va a servir igual.

WhatsApp directo: +34 615 606 285"""

NEW_TITLE = "Fundador & CEO"
NEW_COMPANY = "Sistema 180"


async def human_delay(min_s=1, max_s=3):
    await asyncio.sleep(random.uniform(min_s, max_s))


async def clear_and_type(page, text):
    """Clear field and type with human speed."""
    await page.keyboard.press("Control+A")
    await asyncio.sleep(0.2)
    await page.keyboard.press("Backspace")
    await asyncio.sleep(0.3)
    await human_type(page, text)


async def click_element(page, selector, timeout=5000):
    """Click element with human mouse movement."""
    try:
        el = page.locator(selector).first
        await el.wait_for(state="visible", timeout=timeout)
        box = await el.bounding_box()
        if box:
            target_x = box["x"] + box["width"] * random.uniform(0.3, 0.7)
            target_y = box["y"] + box["height"] * random.uniform(0.3, 0.7)
            await human_click(page, target_x, target_y)
            return True
    except:
        pass
    return False


async def update_headline(page):
    """Update the LinkedIn headline."""
    print("\n  [1/3] Actualizando HEADLINE...")
    
    # Go to profile
    await page.goto(PROFILE_URL, wait_until="domcontentloaded")
    await human_delay(3, 5)
    
    # Click pencil/edit icon on intro section
    edit_btn = page.locator('button[aria-label*="Editar introducción"], button[aria-label*="Edit intro"]')
    if await edit_btn.count() > 0:
        await click_element(page, 'button[aria-label*="Editar introducción"], button[aria-label*="Edit intro"]')
    else:
        # Try the pencil icon near the name
        pencil = page.locator('button.pv-top-card--edit').first
        if await pencil.count() > 0:
            await click_element(page, 'button.pv-top-card--edit')
        else:
            # Click any edit button in the top card
            await click_element(page, 'section.pv-top-card button[type="button"]')
    
    await human_delay(2, 4)
    
    # Find headline field
    headline_field = page.locator('input[id*="headline"], input[aria-label*="Titular"], input[aria-label*="Headline"]')
    if await headline_field.count() > 0:
        box = await headline_field.first.bounding_box()
        if box:
            await human_click(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            await human_delay(0.5, 1)
            await clear_and_type(page, NEW_HEADLINE)
            print("    ✓ Headline actualizado")
    else:
        print("    ✗ No encontré el campo de headline")
        return False
    
    # Save
    save_btn = page.locator('button:has-text("Guardar"), button:has-text("Save")')
    if await save_btn.count() > 0:
        await click_element(page, 'button:has-text("Guardar"), button:has-text("Save")')
        await human_delay(2, 3)
        print("    ✓ Guardado")
    
    return True


async def update_about(page):
    """Update the About section."""
    print("\n  [2/3] Actualizando ABOUT / ACERCA DE...")
    
    await page.goto(PROFILE_URL, wait_until="domcontentloaded")
    await human_delay(3, 5)
    
    # Scroll to About section
    await human_scroll(page, "down", 400)
    await human_delay(1, 2)
    
    # Click edit on About section
    about_edit = page.locator('section:has(h2:has-text("Acerca de")) button, section:has(h2:has-text("About")) button')
    if await about_edit.count() > 0:
        await click_element(page, 'section:has(h2:has-text("Acerca de")) button, section:has(h2:has-text("About")) button')
    else:
        # Try the "Add about" button
        add_about = page.locator('button:has-text("Añadir sección del perfil"), button:has-text("Add profile section")')
        if await add_about.count() > 0:
            await click_element(page, 'button:has-text("Añadir sección del perfil"), button:has-text("Add profile section")')
            await human_delay(1, 2)
            about_option = page.locator('li:has-text("Acerca de"), li:has-text("About")')
            if await about_option.count() > 0:
                await click_element(page, 'li:has-text("Acerca de"), li:has-text("About")')
    
    await human_delay(2, 3)
    
    # Find textarea for About
    about_field = page.locator('textarea[id*="summary"], textarea[aria-label*="Acerca"], textarea[aria-label*="About"]')
    if await about_field.count() > 0:
        box = await about_field.first.bounding_box()
        if box:
            await human_click(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            await human_delay(0.5, 1)
            await clear_and_type(page, NEW_ABOUT)
            print("    ✓ About actualizado")
    else:
        print("    ✗ No encontré el campo About")
        return False
    
    # Save
    save_btn = page.locator('button:has-text("Guardar"), button:has-text("Save")')
    if await save_btn.count() > 0:
        await click_element(page, 'button:has-text("Guardar"), button:has-text("Save")')
        await human_delay(2, 3) 
        print("    ✓ Guardado")
    
    return True


async def update_experience(page):
    """Update current experience title."""
    print("\n  [3/3] Actualizando EXPERIENCIA...")
    
    await page.goto(PROFILE_URL, wait_until="domcontentloaded")
    await human_delay(3, 5)
    
    # Scroll to Experience section
    await human_scroll(page, "down", 600)
    await human_delay(1, 2)
    
    # Look for add experience button or edit existing
    exp_section = page.locator('section:has(h2:has-text("Experiencia")), section:has(h2:has-text("Experience"))')
    
    if await exp_section.count() > 0:
        # Try to add new experience
        add_btn = exp_section.locator('button[aria-label*="Añadir"], button[aria-label*="Add"]').first
        if await add_btn.count() > 0:
            box = await add_btn.bounding_box()
            if box:
                await human_click(page, box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                await human_delay(2, 3)
                
                # Fill title
                title_field = page.locator('input[aria-label*="Cargo"], input[aria-label*="Title"]')
                if await title_field.count() > 0:
                    tbox = await title_field.first.bounding_box()
                    if tbox:
                        await human_click(page, tbox["x"] + tbox["width"] / 2, tbox["y"] + tbox["height"] / 2)
                        await clear_and_type(page, NEW_TITLE)
                        print("    ✓ Título actualizado: {}".format(NEW_TITLE))
                
                await human_delay(1, 2)
                
                # Fill company
                company_field = page.locator('input[aria-label*="Empresa"], input[aria-label*="Company"]')
                if await company_field.count() > 0:
                    cbox = await company_field.first.bounding_box()
                    if cbox:
                        await human_click(page, cbox["x"] + cbox["width"] / 2, cbox["y"] + cbox["height"] / 2)
                        await clear_and_type(page, NEW_COMPANY)
                        print("    ✓ Empresa actualizada: {}".format(NEW_COMPANY))
                
                await human_delay(1, 2)
                
                # Save
                save_btn = page.locator('button:has-text("Guardar"), button:has-text("Save")')
                if await save_btn.count() > 0:
                    await click_element(page, 'button:has-text("Guardar"), button:has-text("Save")')
                    await human_delay(2, 3)
                    print("    ✓ Experiencia guardada")
    
    return True


async def main():
    print("=" * 60)
    print("  LINKEDIN GHOST OPTIMIZER — Sistema 180")
    print("  Perfil: {}".format(PROFILE_URL))
    print("=" * 60)
    
    pw = await async_playwright().start()
    
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=LINKEDIN_PROFILE_DIR,
        channel="msedge",
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--window-position=50,30",
            "--window-size=1280,850",
        ],
        viewport={"width": 1260, "height": 800},
        locale="es-ES",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        ignore_https_errors=True,
    )
    
    page = ctx.pages[0] if ctx.pages else await ctx.new_page()
    await page.add_init_script('Object.defineProperty(navigator,"webdriver",{get:()=>undefined})')
    
    # Navigate to LinkedIn
    await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
    await human_delay(3, 5)
    
    # Check if logged in
    search = page.locator('input[aria-label*="Buscar"], input[aria-label*="Search"]')
    if await search.count() == 0:
        print("\n  [!] No estás logueado. Inicia sesión en la ventana que se abrió.")
        print("  Cuando estés logueado, pulsa Enter...")
        input()
    
    print("\n  ✓ Logueado en LinkedIn")
    
    # Update each section
    await update_headline(page)
    await human_delay(3, 5)
    
    await update_about(page)
    await human_delay(3, 5)
    
    await update_experience(page)
    
    # Final: go back to profile to verify
    await page.goto(PROFILE_URL, wait_until="domcontentloaded")
    await human_delay(3, 5)
    
    print("\n" + "=" * 60)
    print("  ✅ PERFIL LINKEDIN OPTIMIZADO")
    print("  Revisa el resultado en la ventana del navegador")
    print("=" * 60)
    
    print("\n  Pulsa Enter para cerrar...")
    input()
    
    await ctx.close()
    await pw.stop()


if __name__ == "__main__":
    asyncio.run(main())
