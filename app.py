from flask import Flask, request, send_file
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

    # יצירת תמונה
    img = Image.new("RGB", (1080, 1080), color=bg_color)
    draw = ImageDraw.Draw(img)

    # טעינת פונט (נמצא בקובץ עם שם זהה בתיקייה)
    font_path = "NotoSansHebrew-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)

    # חישוב מיקום טקסט (מרכז)
    w, h = draw.textsize(text, font=font)
    draw.text(((1080 - w) / 2, (1080 - h) / 2), text, fill=color, font=font, align="right")

    # שמירה לקובץ
    output_path = "output.png"
    img.save(output_path)

    return send_file(output_path, mimetype="image/png")


# הרצת השרת עם פורט מתאים ל-Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
