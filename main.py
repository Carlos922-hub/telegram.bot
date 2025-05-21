from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import JSONResponse
from PIL import Image, ImageDraw, ImageFont
import io
import os
import telegram
import asyncio

app = FastAPI()

BOT_TOKEN = "8108835149:AAGaPsopra8CtGHp8KI3dgn3lJXB9AjOqio"
CHANNEL = "2642923411"

bot = telegram.Bot(token=BOT_TOKEN)

@app.post("/")
async def telegram_webhook(photo: UploadFile = None):
    if not photo:
        return {"ok": False, "error": "No photo received"}

    contents = await photo.read()
    image = Image.open(io.BytesIO(contents))

    # dodanie watermarka
    watermark = "@BettingProInfo"
    font = ImageFont.truetype("arial.ttf", 28)
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), watermark, font=font, fill=(0, 0, 0, 128))

    # zapisz do bufora
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

    # wyślij do kanału
    await bot.send_photo(chat_id=CHANNEL, photo=buf)
    return {"ok": True}
