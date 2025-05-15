from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import uuid
import datetime

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.json
    text = data.get("text", "אין טקסט")
    image_url = data.get("image_url")
    font_size = int(data.get("font_size", 60))
    color = data.get("color", "#ffffff")

    # הורדת תמונת הרקע
    response = requests.get(image_url)
    background = Image.open(BytesIO(response.content)).convert("RGBA")
    
    # יצירת שכבת טקסט שקופה
    txt_layer = Image.new('RGBA', background.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # טעינת הפונט
    font = ImageFont.truetype("NotoSansHebrew-Regular.ttf", font_size)

    # חישוב מיקום הטקסט
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    text_x = (background.width - text_width) / 2
    text_y = (background.height - text_height) / 2 - 20

    # ציור מלבן שחור חצי שקוף
    padding = 40
    rect_x0 = text_x - padding
    rect_y0 = text_y - padding / 2
    rect_x1 = text_x + text_width + padding
    rect_y1 = text_y + text_height + padding / 2
    draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=(0, 0, 0, 180))

    # ציור הטקסט
    draw.text((text_x, text_y), text, font=font, fill=color)

    # הוספת לוגו
    logo = Image.open("Perfect1-Logo-WhitePerfect1.png").convert("RGBA")
    logo_width = 180
    ratio = logo_width / logo.width
    logo = logo.resize((logo_width, int(logo.height * ratio)))
    logo_x = (background.width - logo.width) // 2
    logo_y = background.height - logo.height - 40
    txt_layer.paste(logo, (logo_x, logo_y), mask=logo)

    # מיזוג שכבות
    final = Image.alpha_composite(background, txt_layer).convert("RGB")

    # שמירה עם שם קובץ ייחודי למחיקה עתידית
    filename = f"output_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join("generated", filename)
    final.save(filepath, format="JPEG")

    return {"url": request.host_url + f"generated/{filename}"}

@app.route("/generated/<filename>")
def serve_generated_image(filename):
    return send_file(os.path.join("generated", filename), mimetype="image/jpeg")

if __name__ == "__main__":
    os.makedirs("generated", exist_ok=True)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
