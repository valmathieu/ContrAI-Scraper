import asyncio
import sys
from playwright.async_api import async_playwright
from prompt_toolkit.shortcuts import button_dialog

# --- CONFIGURATION ---
CIBLED_URL = "https://app.belote-rebelote.fr/"
EMAIL = "contrai-michel@proton.me"
FIXED_CODE = "0343"

async def get_players(page) -> dict:
    """Extracts player names from the 4 cardinal positions."""
    positions = ['nord', 'sud', 'est', 'ouest']
    players = {}

    print("👥 Identifying players...")
    for pos in positions:
        # We construct the selector dynamically: #nord div[data-role="badge"]
        selector = f"#{pos} div[data-role='badge']"

        # Wait a brief moment to ensure UI is rendered
        try:
            name = await page.inner_text(selector, timeout=2000)
            players[pos] = name
        except Exception:
            players[pos] = "Unknown"
            print(f"⚠️ Could not find player name for {pos}")

    print(f"✅ Players found: {players}")
    return players

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

        # --- PHASE 2: TABLE HUNTING LOOP ---
        print("\n🔎 STARTING TABLE ANALYSIS LOOP")

        match_found = False
        max_attempts = 20  # Safety limit to prevent infinite loops
        current_attempt = 0

        while not match_found and current_attempt < max_attempts:
            current_attempt += 1
            print(f"🔄 Check #{current_attempt}: Analyzing table type...")

            # We wait a bit for the table UI to load
            await page.wait_for_timeout(2000)

            # Selector for the Tournament/Target Indicator
            target_selector = '#tournamentMatchInfo'

            # Check if the element exists
            is_target_present = await page.locator(target_selector).is_visible()

            if is_target_present:
                print("✅ TARGET FOUND! This is a Tournament Match.")
                print("🏆 <div id='tournamentMatchInfo'> detected.")
                match_found = True
                # The loop ends here, we stay on this page.
            else:
                print("❌ Standard table detected. Looking for 'Next Table' button...")

                # Selector for "See another table"
                next_table_btn = page.locator('button[data-i18n="gui.online.tables.other-table"]')

                if await next_table_btn.is_visible():
                    print("➡️ Clicking 'See another table'...")
                    await next_table_btn.click()
                    # Wait for the reload
                    print("⏳ Switching tables...")
                    await page.wait_for_timeout(3000)
                else:
                    print("⛔ CRITICAL: 'Next Table' button not found!")
                    print("Maybe we are back in the lobby? Stopping script.")
                    break

        # --- FINAL STATE ---
        if match_found:
            print("\n🎉 SUCCESS: We are observing the correct table type.")

            # 1. Player Identification
            players = await get_players(page)

            await page.screenshot(path="success_target_table.png")
            print("📸 Proof saved as 'success_target_table.png'")
        else:
            print("\nFAILED: Target table not found after max attempts.")

        # Keep browser open for a bit to inspect
        await page.wait_for_timeout(5000)
        await browser.close()
        print("🏁 Script finished.")


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())