# eink_main.py
import time
from inky.auto import auto
from calendar_logic import render as render_calendar
from calendar_logic import WIDTH, HEIGHT
import gpiod
import gpiodevice
# from spotify_logic import render as render_spotify
from gpiod.line import Bias, Direction, Edge

SW_A = 5
SW_B = 6
SW_C = 16
SW_D = 24

BUTTONS = [SW_A, SW_B, SW_C, SW_D]

LABELS = ["A", "B", "C", "D"]

INPUT = gpiod.LineSettings(direction=Direction.INPUT, bias=Bias.PULL_UP, edge_detection=Edge.FALLING)

chip = gpiodevice.find_chip_by_platform()

OFFSETS = [chip.line_offset_from_id(id) for id in BUTTONS]
line_config = dict.fromkeys(OFFSETS, INPUT)

request = chip.request_lines(consumer="spectra6-buttons", config=line_config)

inky_display = auto()
current_mode = "calendar"
last_refresh_time = 0
REFRESH_INTERVAL = 480

def update_display():
    global last_refresh_time
    print(f"Refreshing E-ink in {current_mode} mode...")

    if current_mode == "calendar":
        img = render_calendar(WIDTH,HEIGHT)
    elif current_mode == "spotify":
        #img = render_spotify(WIDTH, HEIGHT)
        print("Spotify mode selected (logic not done)")

    display_img = img.convert("RGB")
    inky_display.set_image(display_img)
    inky_display.show()
    last_refresh_time = time.time()

if __name__ == "__main__":
    update_display()
    while True:
        events = request.wait_edge_events(dt.timedelta(seconds=1))
        if events:
            for event in events:
                offset = event.line_offset
                if offset == OFFSETS[0]:
                    print("Button A: Switching to Calendar")
                    current_mode = "calendar"
                    update_display()
                elif offset == OFFSETS[1]:
                    print("Button B: Switching to Spotify")
                    current_mode = "spotify"
                    update_display()
        if time.time() - last_refresh_time > REFRESH_INTERVAL:
            print("Timer triggered: refresh started")
            update_display()
