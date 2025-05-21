
from fastapi import FastAPI, Request
import httpx
from PIL import Image
from io import BytesIO
import os

app = FastAPI()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL = os.getenv("TARGET_CHANNEL")  # e.g. "@kanalYYY"
WATERMARK_PATH = "telegram_watermark_light.png"

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()

    message = data.get("message", {})
    photo = message.get("photo", [])
    if not photo:
        return {"status": "no photo"}

    # get the highest resolution photo
    file_id = photo[-1]["file_id"]

    async with httpx.AsyncClient() as client:
        file_info = await client.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}")
        file_path = file_info.json()["result"]["file_path"]

        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_data = await client.get(file_url)
        image = Image.open(BytesIO(file_data.content)).convert("RGBA")

        # Load watermark
        watermark = Image.open(WATERMARK_PATH).convert("RGBA")
        wm_resized = watermark.resize(image.size)
        image_with_wm = Image.alpha_composite(image, wm_resized)

        # Send image to target channel
        buffer = BytesIO()
        image_with_wm.save(buffer, format="PNG")
        buffer.seek(0)

        files = {"photo": ("image.png", buffer, "image/png")}
        data = {"chat_id": TARGET_CHANNEL}

        await client.post(f"{TELEGRAM_API_URL}/sendPhoto", data=data, files=files)

    return {"status": "ok"}
