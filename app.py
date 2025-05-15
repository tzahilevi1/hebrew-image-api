from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import glob
import time
from io import BytesIO
import requests

app = Flask(__name__)
FOLDER = "images"
os.makedirs(FOLDER, exist_ok=True)

LOGO_PATH = "Perfect1-Logo-WhitePerfect1.webp"

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.json
    text = data.get("text", "אין טקסט")
    font_size = int(data.get("font_size", 60))
    text_color = data.get("color", "#ffffff")
    bg_color = data.get("bg_color", "#000000")
    image_url = data.get("image_url")

    img = Image.new("RGB", (1080, 1080), color=bg_color)

    if image_url:
        try:
            response = requests.get(image_url)
            background = Image.open(BytesIO(response.content)).resize((1080, 1080)).convert("RGB")
            img.paste(background)
        except:
            pass

    draw = ImageDraw.Draw(img)
    font_path = "NotoSansHebrew-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)

    # חישוב גודל המלל
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # גודל מסגרת שחורה + ריווח
    padding = 40
    box_w = text_w + padding * 2
    box_h = text_h + padding * 2
    box_x = (1080 - box_w) / 2
    box_y = 360  # מעלה את המסגרת משמעותית

    # יצירת שכבת אלפא למסגרת שקופה
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle(
        [(box_x, box_y), (box_x + box_w, box_y + box_h)],
        fill=(0, 0, 0, 180)  # שחור עם שקיפות (0–255)
    )
    img = Image.alpha_composite(img, overlay)

    # ציור הטקסט עם הדגשה
    draw = ImageDraw.Draw(img)
    draw.text(
        ((1080 - text_w) / 2, box_y + padding // 2),
        text,
        fill=text_color,
        font=font,
        align="center",
        direction="rtl",
        stroke_width=2,
        stroke_fill="black"
    )

    # הוספת הלוגו בתחתית התמונה
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        logo_width = 200
        ratio = logo_width / logo.width
        logo = logo.resize((logo_width, int(logo.height * ratio)))
        logo_x = (1080 - logo.width) // 2
        logo_y = 1080 - logo.height - 30
        img.paste(logo, (logo_x, logo_y), logo)
    except Exception as e:
        print(f"Failed to add logo: {e}")

    # שמירה
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(FOLDER, filename)
    img.convert("RGB").save(filepath)

    return jsonify({"url": request.host_url.rstrip("/") + f"/images/{filename}"})

@app.route("/images/<filename>")
def serve_image(filename):
    return send_file(os.path.join(FOLDER, filename), mimetype="image/png")

@app.before_request
def cleanup_old_images():
    now = time.time()
    for file in glob.glob(f"{FOLDER}/*.png"):
        if os.path.isfile(file) and (now - os.path.getmtime(file)) > 7 * 86400:
            try:
                os.remove(file)
            except:
                pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
