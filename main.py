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

    width, height = image.size

    # NAPISY
    texts = ["@BettingProInfo", "@bpadmin11"]

    # Czcionka skalowana
    font_size = int(min(width, height) * 0.045)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Odstępy (inne dla małych formatów)
    if height < 800:
        spacing_x = int(width * 0.6)
        spacing_y = int(height * 0.5)
        watermark_start_y = int(height * 0.25)
    else:
        spacing_x = int(width * 0.35)
        spacing_y = int(height * 0.25)
        watermark_start_y = int(height * 0.35)

    # Tworzenie warstwy z watermarkami
    watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    i = 0
    for x in range(0, width, spacing_x):
        j = 0
        for y in range(watermark_start_y, height, spacing_y):
            current_text = texts[(i + j) % 2]
            draw.text((x, y), current_text, font=font, fill=(255, 255, 255, 45))
            j += 1
        i += 1

    # Obracanie watermarka
    rotated = watermark_layer.rotate(22, expand=1)
    watermark_cropped = rotated.crop(rotated.getbbox()).resize(image.size)
    watermarked = Image.alpha_composite(image, watermark_cropped)

    # Bufor i wysyłka
    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)

    await bot.send_photo(chat_id=CHANNEL, photo=buf)
    return {"ok": True}
