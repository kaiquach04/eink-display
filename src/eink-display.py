import os.path
import datetime as dt
import io
import time
from dotenv import load_dotenv
from flask import Flask, Response
from PIL import Image, ImageDraw, ImageFont
from font_fredoka_one import FredokaOne
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import defaultdict
from inky.auto import auto

try:
   inky_display = auto()
except ImportError:
   inky_display = None
   print("Library not found")

SCOPES = ["https://www.googleapis.com/auth/calendar"]
app = Flask(__name__)
load_dotenv()
CALENDAR_ID = os.getenv("KAI_EM_CALENDAR_ID")

# holy measurements
WIDTH, HEIGHT = 800, 480  # Inky Impression 7.3"
HEADER_H = 35
TIME_W = 50
GRID_Y0 = 50 #TOP OF GRID AREA
GRID_H = HEIGHT - HEADER_H
DAY_X0 = 50 #START OF DAY AREA
DAY_W_TOTAL = WIDTH - TIME_W

ROW_H = 445 / 12
DAY_W = 750 / 7

BLUE = "#212842"
CREAM = "#F0E7D5"
MIDNIGHT = "#181C30"
SAGE = "#8FAF9A"     # muted green (calm, natural accent)
CLAY = "#C47A5A"     # soft terracotta (warm highlight / CTA)
SLATE = "#6E7387"    # cool gray-blue (neutral text, borders)

DAY_DICT = {"Sunday": 0, "Monday": 1, "Tuesday": 2, "Wednesday": 3, "Thursday": 4, "Friday": 5, "Saturday": 6}
TIME_DICT = {"all-day": 0, "08": 1, "09": 2, "10": 3, "11": 4, "12": 5, "01": 6, "02": 7, "03": 8, "04": 9, "05": 10 }


def get_y_pos(time_str):
    if time_str == "All Day":
        return HEADER_H + ROW_H # Top row
    
    # Parse the string 
    time_part, period = time_str.split(' ')
    hours, minutes = map(int, time_part.split(':'))
    
    # Convert to 24-hour format for easier math
    if period == "PM" and hours != 12:
        hours += 12
    if period == "AM" and hours == 12:
        hours = 0
        
    # Calculate minutes past your calendar start (e.g., 7:00 AM)
    CALENDAR_START_HOUR = 8
    total_minutes = (hours - CALENDAR_START_HOUR) * 60 + minutes
    
    base_offset = HEADER_H + (2 * ROW_H)
    # Map to Pixels
    # Every 60 minutes = 1 ROW_H. Plus 1 because the first row is 'All-day'
    total_minutes = (hours - CALENDAR_START_HOUR) * 60 + minutes
    y_pos = base_offset + (total_minutes / 60) * ROW_H
    return y_pos

def draw_rect(day, start_time, end_time, summary, timeFont, draw):
  day_val = DAY_DICT[day]
  
  # Calculate X (Columns)
  col_start = (day_val * DAY_W) + TIME_W
  col_margin = 5  # Padding so rectangles don't touch divider lines
  x1 = col_start + col_margin
  x2 = col_start + DAY_W - col_margin

  # Calculate Y (Rows)
  if start_time == "All Day":
      row_start = HEADER_H + (0 * ROW_H)
      row_center = (row_start + (ROW_H / 2)) + ROW_H
      y1 = row_center - 15
      y2 = row_center + 15
  else:
      y1 = get_y_pos(start_time)
      y2 = get_y_pos(end_time)

  # Draw the block
  draw.rounded_rectangle([x1, y1, x2, y2], radius=8, fill=SLATE, outline=CREAM)
  
  # Draw text inside the block
  # Center text between y1 and y2
  text_y = (y1 + y2) / 2
  text_x = (x1 + x2) / 2
  draw.text((text_x, text_y), summary[:12], fill=CREAM, font=timeFont, anchor="mm")
  

def format_event_time(time_str):
  if not time_str:
    return ""
  
  if len(time_str) <= 10:
    return "All Day"
  
  dt_obj = dt.datetime.fromisoformat(time_str.replace("Z", "+00:00"))
  return dt_obj.strftime("%I:%M %p")

def render(width: int, height: int) -> Image.Image:
  creds = None

  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json")

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
      creds = flow.run_local_server(port=0)

      with open("token.json", "w") as token:
          token.write(creds.to_json())

  try:
      service = build("calendar", "v3", credentials=creds)

      today = dt.datetime.now(dt.UTC)
      days_since_monday = today.weekday()
      start_of_week = today - dt.timedelta (days=days_since_monday)
      start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)

      end_of_week= start_of_week + dt.timedelta(days=6)
      end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=0)

      timeMin = start_of_week.isoformat().replace("+00:00", "Z")
      timeMax = end_of_week.isoformat().replace("+00:00", "Z")

      event_result = service.events().list(calendarId=CALENDAR_ID, timeMin=timeMin, timeMax=timeMax, singleEvents=True, orderBy="startTime").execute()
      events = event_result.get("items", [])

      if not events:
        print("no upcoming events found")
        return
      
      weekly_list = []
      for event in events:
        start = event["start"].get("dateTime") or event["start"].get("date")
        end = event["end"].get("dateTime") or event["end"].get("date")
        summary = event.get("summary", "(No Title)")

        event_date = dt.datetime.fromisoformat(start[:10])
        weekly_list.append({
          "day": event_date.strftime("%A"),
          "start": format_event_time(start),
          "end": format_event_time(end),
          "summary": summary,
          "is_all_day": "dateTime" not in event["start"]
        })

      img = Image.new("RGB", (width, height), MIDNIGHT) # Creates the background
      draw = ImageDraw.Draw(img)
      draw.rectangle([0, 0, width, HEADER_H], fill=BLUE) # Header
      font_path = FredokaOne
      font2 = ImageFont.truetype(font_path, size=15) # font size for header
      timeFont = ImageFont.truetype(font_path, size=10) # Font size for main calendar

      events_by_day = defaultdict(list)
      for event in weekly_list:
        events_by_day[event["day"]].append(event)

      days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
      time_frame = ["all-day", "8am", "9am", "10am", "11am", "12pm", "1pm", "2pm", "3pm", "4pm", "5pm"]
      week_range = f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"

      draw.text((20, 10), "Kai + Em Calendar", fill=CREAM, font=font2)
      draw.text((WIDTH - 20, 10), week_range, fill=CREAM, font=font2, anchor="ra")
      draw.line([(TIME_W, HEADER_H), (TIME_W, height)], fill=CREAM, width=1) # Creates the vertical line for the time_frame
      
      for i, time in enumerate(time_frame): # Creates all of the rows necessary for time_frame
        h = (i * ROW_H) + HEADER_H 

        if i > 0:
          draw.line([(0, h), (width, h)], fill=CREAM, width=1)

        text_center_y = (h + (ROW_H / 2)) + ROW_H 
        draw.text((TIME_W / 2, text_center_y), time, fill=CREAM, font=timeFont, anchor="mm") 

      # Create bottom line for row
      bottom_line_y = HEADER_H + (11 * ROW_H)
      draw.line([(0, bottom_line_y), (width, bottom_line_y)], fill=CREAM, width=1) 

      today_name = dt.datetime.now().strftime("%A")
      # Creates the rest of the vertical lines for the following days
      for i, d in enumerate(days):
        x_start = (i * DAY_W) + TIME_W
        text_center_x = (x_start + (DAY_W / 2)) 

        if i > 0:
          draw.line([(x_start, HEADER_H), (x_start, height)], fill=CREAM, width=1)
        if d == today_name: 
          # Draw the highlight rectangle
          draw.rectangle([x_start, HEADER_H, x_start + DAY_W, HEADER_H + ROW_H], fill=CREAM)
          draw.text((text_center_x, HEADER_H + 20), d[:3].upper(), fill=BLUE, font=font2, anchor="ms")
        else:
          draw.rectangle([x_start, HEADER_H, x_start + DAY_W, HEADER_H + ROW_H], fill=BLUE, outline=CREAM)
          draw.text((text_center_x, HEADER_H + 20), d[:3].upper(), fill=CREAM, font=font2, anchor="ms")

        y_offset = HEADER_H + 45
        day_events = events_by_day.get(d, [])

        for event in day_events: # Loops through the following events for correlated day in the loop
          if y_offset > height - 20:
            break
          
          draw_rect(event["day"], event["start"], event["end"], event["summary"], timeFont, draw)
      
      return img

  except HttpError as error:
      print("An error occurred:", error)

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
      }}, 600000);
    </script>
  </body>
</html>"""

@app.get("/render.png")
def render_png():
    img = render(WIDTH, HEIGHT)
    if inky_display:
       pal_img = img.convert("P", pallete=Image.ADAPTIVE, colors=7)

       inky_display.set_image(pal_img)
       inky_display.show()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    # debug=True auto-reloads server when you save code
    app.run(host="127.0.0.1", port=5000, debug=True)
