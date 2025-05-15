from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import uuid
import glob
import time

app = Flask(__name__)

FOLDER = "images"
os.makedirs(FOLDER, exist_ok=True)  # יצירת תקייה אם לא קיימת

@app.route("/generate", methods=["POST"])
def generate_image():
    # קבלת נתונים מהבקשה
    data = request.json
    text = data.get("text", "אין טקסט")
    font_size = int(data.get("font_size", 60))
    color = data.get("color", "#ffffff")  # לבן כברירת מחדל
    bg_color = data.get("bg_color", "#000000")
    image_url = data.get("image_url")  # אפשרי, למקרה שתרצה להשתמש כרקע

    # יצירת תמונה חדשה
    img = Image.new("RGB", (1080, 1080), color=bg_color)

    # אם הוזן רקע מתמונה – נטען ונשים אותו
    if image_url:
        try:
            from io import BytesIO
            import requests
            response = requests.get(image_url)
            background = Image.open(BytesIO(response.content)).resize((1080, 1080)).convert("RGB")
            img.paste(background)
        except:
            pass  # אם נכשל, נמשיך עם רקע רגיל

    draw = ImageDraw.Draw(img)
    font_path = "NotoSansHebrew-Regular.ttf"
    font = ImageFont.truetype(font_path, font_size)

    # חישוב מיקום מרכזי למלל
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (1080 - w) / 2
    y = (1080 - h) / 2

    draw.text((x, y), text, fill=color, font=font, align="right", direction="rtl")

    # יצירת שם קובץ ייחודי
    filename = f"{uuid.uuid4().hex}.png"
    filepath = os.path.join(FOLDER, filename)
    img.save(filepath)

    # החזרת קישור לקובץ
    file_url = request.host_url.rstrip("/") + f"/images/{filename}"
    return jsonify({"url": file_url})

@app.route("/images/<filename>")
def serve_image(filename):
    filepath = os.path.join(FOLDER, filename)
    return send_file(filepath, mimetype="image/png")

# קריאה פנימית לניקוי קבצים ישנים – מחיקת קבצים בני יותר מ־7 ימים
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
