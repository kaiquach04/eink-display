import os.path
import datetime as dt
import io
import time
from flask import Flask, Response
from calendar_logic import render, WIDTH, HEIGHT
app = Flask(__name__)

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


@app.route("/render.png")
def render_png():
    img = render(WIDTH, HEIGHT)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    render(WIDTH, HEIGHT)
    app.run(host="127.0.0.1", port=5000, debug=True)