from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
import io
import telegram

app = FastAPI()

BOT_TOKEN = "8108835149:AAGaPsopra8CtGHp8KI3dgn3lJXB9AjOqio"
CHANNEL = -1002642923411

bot = telegram.Bot(token=BOT_TOKEN)

@app.post("/")
async def telegram_webhook(photo: UploadFile = None):
    if not photo:
        return JSONResponse(content={"ok": False, "error": "No photo received"}, status_code=400)

    contents = await photo.read()
    image = Image.open(io.BytesIO(contents)).convert("RGBA")

    # Konfiguracja watermarka
    text = "@BettingProInfo"
    width, height = image.size

    # Dynamiczne skalowanie czcionki i siatki
    font_size = int(min(width, height) * 0.04)  # 4% wysokości zdjęcia
    font = ImageFont.load_default()

    spacing_x = int(width * 0.25)  # co 25% szerokości
    spacing_y = int(height * 0.15)  # co 15% wysokości

    # Warstwa z watermarkiem
    watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    for x in range(0, width, spacing_x):
        for y in range(0, height, spacing_y):
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 40))

    # Obrót watermarka o 35°
    rotated = watermark_layer.rotate(35, expand=1)
    watermark_cropped = rotated.crop(rotated.getbbox()).resize(image.size)

    # Połączenie z oryginalnym zdjęciem
    watermarked = Image.alpha_composite(image, watermark_cropped)

    # Bufor i wysyłka
    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)

    await bot.send_photo(chat_id=CHANNEL, photo=buf)
    return {"ok": True}
