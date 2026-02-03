# eink_main.py
import time
from inky.auto import auto
from calendar_logic import render, WIDTH, HEIGHT

inky_display = auto()

def update_display():
    print("Refreshing E-ink...")
    img = render(WIDTH, HEIGHT)
    display_img = img.convert("RGB")
    inky_display.set_image(display_img)
    inky_display.show()

if __name__ == "__main__":
    while True:
        try:
            update_display()
        except Exception as e:
            print(f"Update failed: {e}")
        time.sleep(480) # Wait 8 minutes