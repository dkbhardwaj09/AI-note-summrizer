import asyncio
from playwright.async_api import async_playwright, expect

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        try:
            # Navigate to the login page
            await page.goto("http://127.0.0.1:8000/login")

            # Expect the "Login" heading to be visible
            await expect(page.get_by_role("heading", name="Login")).to_be_visible(timeout=5000)

            # Take a screenshot of the login page
            await page.screenshot(path="jules-scratch/verification/login_page.png")
            print("Successfully captured screenshot of the login page.")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())