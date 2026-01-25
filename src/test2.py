from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne


inky_display = auto()

img = Image.open("../public/em.jpg")
inky_display.set_image(img)
inky_display.show()
