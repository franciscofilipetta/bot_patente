import asyncio
import os
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from scraper import consultar_multas_cordoba
from aiohttp import web
from scraper import consultar_multas_cordoba

# Cargar variables de entorno (Token)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("No se encontró el BOT_TOKEN en el archivo .env")

# Inicializar bot y dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Regex para validar patentes (Autos viejos, autos nuevos, motos nuevas)
# Ejemplo: AAA 111, AA 111 AA, A 111 AAA, 111 AAA
PATENTE_REGEX = re.compile(r'^[A-Z]{2}\s?\d{3}\s?[A-Z]{2}$|^[A-Z]{3}\s?\d{3}$|^[A-Z]{1}\s?\d{3}\s?[A-Z]{3}$|^\d{3}\s?[A-Z]{3}$', re.IGNORECASE)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """Manejador del comando /start"""
    bienvenida = (
        "👋 ¡Hola! Soy el bot de consulta de multas (Rentas Córdoba - Caminera).\n\n"
        "Enviame la patente de tu auto o moto para verificar si tiene deudas.\n"
        "Formatos válidos: AB123CD, ABC123, A123BCD, 123ABC."
    )
    await message.answer(bienvenida)

@dp.message()
async def check_patente_handler(message: types.Message) -> None:
    """Manejador de mensajes de texto, procesa la patente"""
    texto_usuario = message.text.strip().replace("-", "").replace(" ", "").upper()
    
    # Validar formato
    if not PATENTE_REGEX.match(texto_usuario):
        await message.answer("❌ Formato de patente inválido. Por favor, enviá una patente real de Argentina.")
        return

    # Avisar al usuario que estamos consultando
    wait_msg = await message.answer(f"🔍 Consultando la patente *{texto_usuario}* en la base de Rentas Córdoba. Esto puede demorar unos segundos...", parse_mode="Markdown")
    
    try:
        # Ejecutar el scraper de forma asíncrona
        resultado = await consultar_multas_cordoba(texto_usuario)
        
        if resultado["error"]:
            respuesta_final = f"⚠️ Ocurrió un error al consultar:\n{resultado['mensaje']}"
        elif resultado["deuda"]:
            respuesta_final = (
                f"🚨 **ATENCIÓN** 🚨\n\n"
                f"🚗 Patente: `{texto_usuario}`\n"
                f"💰 Total adeudado: **{resultado['monto']}**\n\n"
                f"Podés ver más detalles y pagar en el portal oficial de Rentas Córdoba."
            )
        else:
            respuesta_final = (
                f"✅ **LIBRE DE MULTAS** ✅\n\n"
                f"🚗 Patente: `{texto_usuario}`\n"
                f"🎉 No se registran deudas en la Policía Caminera (Rentas Córdoba)."
            )
            
    except Exception as e:
        respuesta_final = f"❌ Ocurrió un error inesperado al consultar la página oficial."
        print(f"Error en scraper: {e}")

    # Editar el mensaje de "espera" con el resultado final
    await wait_msg.edit_text(respuesta_final, parse_mode="Markdown")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def init_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render usa la variable PORT, si no está, usamos 8080
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Servidor web de salud iniciado en el puerto {port}")

async def main() -> None:
    # Iniciar el servidor web dummy para pasar los checks de Render
    await init_web_server()
    
    # Iniciar polling del bot
    print("Bot iniciado. Esperando mensajes...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
