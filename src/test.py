from inky.auto import auto
from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne



inky_display = auto()

img = Image.new("P", (inky_display.width, inky_display.height), inky_display.WHITE)
draw= ImageDraw.Draw(img)

font = ImageFont.truetype(FredokaOne, 48)

message = "Hello, World!"
_, _, w, h = font.getbbox(message)
x = (inky_display.width / 2) - (w / 2)
y = (inky_display.height / 2) - (h / 2)

draw.text((x, y), message, inky_display.BLACK, font)
inky_display.set_image(img)
inky_display.show()

