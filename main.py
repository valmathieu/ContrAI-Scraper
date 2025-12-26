import asyncio
import sys
from playwright.async_api import async_playwright
from prompt_toolkit.shortcuts import button_dialog

# --- CONFIGURATION ---
CIBLED_URL = "https://app.belote-rebelote.fr/"
EMAIL = "contrai-michel@proton.me"
FIXED_CODE = "0343"


async def main():
    print("🚀 Bot starts...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        page = await browser.new_page()

        print(f"🌐 Navigation to {CIBLED_URL}...")
        await page.goto(CIBLED_URL)

        # --- LE FREIN À MAIN ---
        print("🛑 STOP ! Waiting 5 seconds that loading finishes...")
        await page.wait_for_timeout(5000)
        print("🟢 Script starts again.")

        # --- STEP 1 : FERMER LE TUTORIEL ---
        print("👀 Check 'Non merci' button...")

        button_tutorial = 'button[data-i18n="gui.quick-start.launch.no"]'

        if await page.locator(button_tutorial).is_visible():
            print("✅ Button visible ! I click.")
            await page.click(button_tutorial)
        else:
            print("❌ Button still invisible despite waiting 5s.")

            # --- PHOTO DIAGNOSTIC ---
            print("📸 I take a screenshot of what I see (debug_tutorial_button.png)")
            await page.screenshot(path="debug_tutorial_button.png")

        # --- STEP 2 : SELECT EMAIL CONNEXION ---
        print("🖱️ Email button search...")

        try:
            bouton_email = page.locator('button[data-icon="email"]')
            await bouton_email.wait_for(state="visible", timeout=5000)
            await bouton_email.click()
            print("✅ Email button clicked.")
        except:
            print("❌ CRITICAL ERROR: Unable to find the 'Email' button.")
            await browser.close()
            return

        # --- STEP 3 : EMAIL INPUT ---
        print(f"✍️ Email input...")
        await page.fill('input[type="email"]', EMAIL)
        await page.click('button[data-i18n="gui.users.email-wizard.continue"]')

        # --- STEP 4 : CODE ---
        await page.wait_for_selector('#verificationCode', state="visible")
        print(f"🤖 Code input : {FIXED_CODE}")
        await page.fill('#verificationCode', FIXED_CODE)
        await page.click('#validateBtn')

        # --- STEP 5 : ONLINE MODE ---
        bouton_online_mode = page.locator('button[data-i18n="gui.actions.mode.online"]')
        await bouton_online_mode.wait_for(state="visible", timeout=5000)
        await bouton_online_mode.click()
        print("✅ Mode Online Button clicked.")

        # --- STEP 6 : ONLINE SPECTATOR MODE ---
        bouton_online_spectator = page.locator('button[data-i18n="gui.actions.online.observe"]')
        await bouton_online_spectator.wait_for(state="visible", timeout=5000)
        await bouton_online_spectator.click()
        print("✅ Online Spectator Button clicked.")

        # --- STEP 7 : CONTREE SPECTATOR MODE ---
        bouton_spectator_contree = page.locator('button[data-i18n="gui.versions.contree"]')
        await bouton_spectator_contree.wait_for(state="visible", timeout=5000)
        await bouton_spectator_contree.click()
        print("✅ Contree Spectator Button clicked.")

        # --- FIN ---
        print("⏳ Arrival in Lobby...")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="lobby_final.png")
        print("🏁 Finished.")

        await browser.close()


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())