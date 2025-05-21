from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
import io
import telegram
import random

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
    colors = [(255, 255, 255, 45), (0, 0, 0, 40)]

    font_size = int(min(width, height) * 0.045)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    watermark_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark_layer)

    # Losowa liczba watermarków (np. 10–20)
    watermark_count = random.randint(10, 20)

    for _ in range(watermark_count):
        x = random.randint(0, width - font_size * 10)
        y = random.randint(int(height * 0.2), height - font_size)
        text = random.choice(texts)
        color = random.choice(colors)
        draw.text((x, y), text, font=font, fill=color)

    # Stały obrót całej warstwy (lub też losowy, jeśli chcesz)
    rotated = watermark_layer.rotate(22, expand=1)
    watermark_cropped = rotated.crop(rotated.getbbox()).resize(image.size)
    watermarked = Image.alpha_composite(image, watermark_cropped)

    buf = io.BytesIO()
    watermarked.save(buf, format="PNG")
    buf.seek(0)

    await bot.send_photo(chat_id=CHANNEL, photo=buf)
    return {"ok": True}
