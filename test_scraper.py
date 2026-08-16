import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print("Navegando a Rentas Cordoba...")
        try:
            await page.goto("https://www.rentascordoba.gob.ar/mirentas/caminera.html", timeout=60000)
            await page.wait_for_load_state('networkidle')
            print("Página cargada.")
            html = await page.content()
            
            # Buscar inputs en el HTML
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            inputs = soup.find_all('input')
            print("Inputs encontrados:")
            for inp in inputs:
                print(f"  - id: {inp.get('id')}, type: {inp.get('type')}, name: {inp.get('name')}")
                
            buttons = soup.find_all('button')
            print("Buttons encontrados:")
            for btn in buttons:
                print(f"  - id: {btn.get('id')}, text: {btn.text.strip()}")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
