from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
import os

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.json
    text = data.get("text", "אין טקסט")
    image_url = data.get("image_url")
    font_size = int(data.get("font_size", 60))
    color = data.get("color", "#ffffff")
    bg_color = data.get("bg_color", "#000000")

    # הורדת תמונה
    if image_url:
        response = requests.get(image_url)
        with open("background.png", "wb") as f:
            f.write(response.content)
        img = Image.open("background.png").convert("RGB")
    else:
        img = Image.new("RGB", (1080, 1080), color=bg_color)

    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("NotoSansHebrew-Regular.ttf", font_size)

    # חישוב מיקום הטקסט
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    padding = 30

    x = (img.width - text_w) / 2
    y = (img.height - text_h) / 2

    # ציור רקע שקוף מאחורי הטקסט
    rect_x1 = x - padding
    rect_y1 = y - padding
    rect_x2 = x + text_w + padding
    rect_y2 = y + text_h + padding
    draw.rectangle([rect_x1, rect_y1, rect_x2, rect_y2], fill=(0, 0, 0, 180))

    # ציור טקסט
    draw.text((x, y), text, fill=color, font=font, align="center")

    output_path = "output.png"
    img.save(output_path)
    url = request.host_url.replace("http://", "https://").rstrip("/") + "/output.png"
    return url, 200, {"Content-Type": "text/plain"}

@app.route("/output.png")
def serve_image():
    return send_file("output.png", mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
