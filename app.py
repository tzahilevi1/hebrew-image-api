from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.json
    text = data.get("text", "אין טקסט")
    font_size = int(data.get("font_size", 60))
    color = data.get("color", "#000000")
    bg_color = data.get("bg_color", "#ffffff")

    img = Image.new("RGB", (1080, 1080), color=bg_color)
    draw = ImageDraw.Draw(img)

    font_path = "NotoSansHebrew-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    draw.text(((1080 - w) / 2, (1080 - h) / 2), text, fill=color, font=font, align="right")

    output_path = "output.png"
    img.save(output_path)

    # החזרת קישור ציבורי לקובץ
    file_url = request.host_url.rstrip("/") + "/output.png"
    return jsonify({"url": file_url})

@app.route("/output.png")
def serve_image():
    return send_file("output.png", mimetype="image/png")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
