import asyncio
import sys
from playwright.async_api import async_playwright

# --- CONFIGURATION ---
URL_CIBLE = "https://app.belote-rebelote.fr/"
MON_EMAIL = "contrai-michel@proton.me"
CODE_FIXE = "0343"


async def main():
    print("🚀 Démarrage du robot...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)  # slow_mo ralentit chaque action de 0.5s
        page = await browser.new_page()

        print(f"🌐 Navigation vers {URL_CIBLE}...")
        await page.goto(URL_CIBLE)

        # --- SÉCURITÉ 1 : On attend que le réseau se calme (fin du chargement) ---
        print("⏳ Attente du chargement complet de la page (Network Idle)...")
        try:
            # Cette ligne est magique pour les Single Page Apps
            await page.wait_for_load_state("networkidle", timeout=15000)
        except:
            print("⚠️ Le chargement est long, mais on tente quand même.")

        # --- ÉTAPE 1 : FERMER LE TUTORIEL ---
        print("👀 Recherche du tutoriel...")
        bouton_tuto = page.locator('button[data-i18n="gui.quick-start.launch.no"]')

        # SÉCURITÉ 2 : On augmente le temps à 10 secondes (10000ms)
        est_visible = await bouton_tuto.is_visible(timeout=10000)

        if est_visible:
            print("✅ Bouton 'Non merci' trouvé ! Clic en cours...")
            await bouton_tuto.click()
            await page.wait_for_timeout(1000)  # Petite pause pour laisser l'animation se finir
        else:
            print("ℹ️ Bouton 'Non merci' absent après 10s d'attente. On continue.")

        # --- ÉTAPE 2 : SÉLECTIONNER CONNEXION EMAIL ---
        print("🖱️ Recherche du bouton Email...")

        # Je remets la tentative par Texte qui est souvent plus sûre
        try:
            # On attend explicitement que le bouton soit cliquable
            bouton_email = page.locator('button[data-icon="email"]')
            await bouton_email.wait_for(state="visible", timeout=5000)
            await bouton_email.click()
            print("✅ Bouton Email cliqué.")
        except:
            print("❌ ERREUR CRITIQUE : Impossible de trouver le bouton 'Email'.")
            # C'est ici qu'il me faut le HTML si ça plante
            await page.screenshot(path="debug_erreur_bouton.png")
            await browser.close()
            return

        # --- ÉTAPE 3 : SAISIE DE L'EMAIL ---
        print(f"✍️ Saisie de l'email...")
        await page.fill('input[placeholder="Adresse électronique"]', MON_EMAIL)
        await page.click('button[data-i18n="gui.users.email-wizard.continue"]')

        # --- ÉTAPE 4 : CODE ---
        await page.wait_for_selector('#verificationCode', state="visible")
        print(f"🤖 Code : {CODE_FIXE}")
        await page.fill('#verificationCode', CODE_FIXE)
        await page.click('#validateBtn')

        # --- FIN ---
        print("⏳ Arrivée au Lobby...")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="lobby_final.png")
        print("🏁 Fini.")

        await browser.close()


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())