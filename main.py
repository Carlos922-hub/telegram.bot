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
    texts = ["@BettingProInfo", "@bpadmin11"]
    kolory = [(255, 255, 255, 45), (0, 0, 0, 40)]  # jasny / ciemny

    # Dynamiczna czcionka
    font_size = int(min(width, height) * 0.045)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Odstępy i minimum siatki
    min_columns = 3
    min_rows = 4
    spacing_x = max(int(width / min_columns), 250)
    spacing_y = max(int(height / min_rows), 150)
    watermark_start_y = int(height * 0.25)

    watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    for i, x in enumerate(range(0, width, spacing_x)):
        for j, y in enumerate(range(watermark_start_y, height, spacing_y)):
            offset_y = int(spacing_y * 0.4) if (i % 2 == 1) else 0
            text = texts[(i + j) % 2]
            color = kolory[(i + j) % 2]
            draw.text((x, y + offset_y), text, font=font, fill=color)

    rotated = watermark_layer.rotate(22, expand=1)
    watermark_cropped = rotated.crop(rotated.getbbox()).resize(image.size)
    watermarked = Image.alpha_composite(image, watermark_cropped)

    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)

    await bot.send_photo(chat_id=CHANNEL, photo=buf)
    return {"ok": True}
