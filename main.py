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
    image = Image.open(io.BytesIO(contents))


    draw = ImageDraw.Draw(image)
    text = "@BettingProInfo"
    draw.text((10, 10), text, fill=(0, 0, 0))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)

    await bot.send_photo(chat_id=CHANNEL, photo=buf)
    return {"ok": True}
