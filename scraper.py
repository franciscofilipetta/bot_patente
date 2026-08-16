import asyncio
from playwright.async_api import async_playwright

async def consultar_multas_cordoba(patente: str) -> dict:
    """
    Consulta real a Rentas Córdoba (Multas Caminera) usando Playwright.
    """
    resultado = {
        "error": False,
        "deuda": False,
        "monto": "Consultar detalles en la web oficial",
        "mensaje": "No registra deuda"
    }
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # Navegar directamente a la sección de Caminera de Rentas Córdoba
            await page.goto("https://www.rentascordoba.gob.ar/emision/ver-y-pagar/caminera", timeout=45000)
            await page.wait_for_load_state('networkidle')
            
            # Esperar a que aparezca el input de la patente
            input_selector = 'input.form-control'
            await page.wait_for_selector(input_selector, timeout=15000)
            
            # Limpiar el input y escribir la patente
            await page.fill(input_selector, patente)
            
            # Click en Consultar
            btn_consultar = 'button:has-text("Consultar")'
            await page.wait_for_selector(btn_consultar)
            await page.click(btn_consultar)
            
            # Hay dos posibles resultados que cambian el DOM
            # Opción 1: No hay deudas (Aparece un texto rojo en la misma página)
            # Opción 2: Hay deudas (Navega a otra página '/emision/ver-y-pagar/caminera/detalle-de-cuota')
            
            try:
                # Esperamos concurrentemente a que pase una de las dos cosas
                async with page.expect_navigation(url='**/detalle-de-cuota', timeout=10000):
                    # Si navegó a detalle-de-cuota, entonces HAY DEUDA
                    resultado["deuda"] = True
                    resultado["mensaje"] = "Se encontraron infracciones o multas de Caminera pendientes de pago."
            except Exception:
                # Si no navegó, probablemente apareció el cartel de que no hay deuda
                try:
                    # Buscamos el texto de sin deuda
                    await page.wait_for_selector('text="No se encontró información de deuda de Caminera registrada."', timeout=5000)
                    resultado["deuda"] = False
                    resultado["mensaje"] = "No se encontró información de deuda de Caminera registrada."
                except Exception:
                    # Si no navegó y no apareció el cartel, algo falló en la web oficial
                    resultado["error"] = True
                    resultado["mensaje"] = "No se pudo determinar el estado. Es posible que el portal esté congestionado."
                    
            await browser.close()
            
    except Exception as e:
        resultado["error"] = True
        resultado["mensaje"] = f"Error conectando con Rentas Córdoba: {str(e)}"
        
    return resultado
