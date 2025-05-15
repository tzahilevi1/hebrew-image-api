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
    color = data.get("color", "#000000")

    # שלב 1 – הורדת תמונה מ-URL אם קיים, אחרת רקע לבן
    if image_url:
        response = requests.get(image_url)
        with open("background.png", "wb") as f:
            f.write(response.content)
        img = Image.open("background.png").convert("RGB")
    else:
        img = Image.new("RGB", (1080, 1080), color="#ffffff")

    draw = ImageDraw.Draw(img)
    font_path = "NotoSansHebrew-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)

    # חישוב מיקום הטקסט
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (img.width - w) / 2
    y = (img.height - h) / 2

    draw.text((x, y), text, fill=color, font=font, align="center")

    output_path = "output.png"
    img.save(output_path)

    file_url = request.host_url.replace("http://", "https://").rstrip("/") + "/output.png"
    return file_url, 200, {"Content-Type": "text/plain"}

@app.route("/output.png")
def serve_image():
    return send_file("output.png", mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
