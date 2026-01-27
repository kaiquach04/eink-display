import io
import time
from flask import Flask, Response
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
app = Flask(__name__)

WIDTH, HEIGHT = 800, 480  # Inky Impression 7.3"

def render(width: int, height: int) -> Image.Image:
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    font_path = FredokaOne
    font2 = ImageFont.truetype(font_path, size=15)

    # Demo content (replace later with calendar data)
    now = time.strftime("%a %b %d, %I:%M:%S %p")
    title = "E-ink Calendar"
    subtitle = f"Local time: {now}"

    draw.text((24, 14), title, fill="black", font=font2)
    draw.text((36, 54), subtitle, fill="black", font=font)

    # Simple layout boxes to help you design
    draw.rectangle([24, 40, 776, 456], outline="black", width=2)
    draw.text((36, 74), "Calendar block goes here", fill="black", font=font)

    # draw.rectangle([24, 250, 776, 456], outline="black", width=2)
    # draw.text((36, 262), "Other widgets go here", fill="black", font=font)

    return img

@app.get("/")
def index():
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>E-ink Preview</title>
    <style>
      body {{ font-family: system-ui, sans-serif; padding: 16px; }}
      .frame {{ display: inline-block; border: 1px solid #ccc; padding: 8px; }}
      img {{ image-rendering: pixelated; }}
      .hint {{ color: #666; margin-top: 8px; }}
    </style>
  </head>
  <body>
    <h2>E-ink Live Preview (800×480)</h2>
    <div class="frame">
      <img id="screen" width="{WIDTH}" height="{HEIGHT}" src="/render.png?t={time.time()}" />
    </div>
    <div class="hint">
      Auto-refreshes every 1s. Edit <code>render()</code> and refresh the page if needed.
    </div>

    <script>
      const img = document.getElementById("screen");
      setInterval(() => {{
        img.src = "/render.png?t=" + Date.now(); // cache-bust
      }}, 1000);
    </script>
  </body>
</html>"""

@app.get("/render.png")
def render_png():
    img = render(WIDTH, HEIGHT)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    # debug=True auto-reloads server when you save code
    app.run(host="127.0.0.1", port=5000, debug=True)
