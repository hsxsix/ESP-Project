# preview
import os
from PIL import Image, ImageFont, ImageDraw

weather_img = Image.open('./1.png').convert('RGBA')
r,g,b,a = weather_img.split()

bg_img = Image.open('./timg128x96.jpeg')

img = Image.new('RGBA', (128,96), (0,0,0,255))
draw = ImageDraw.Draw(img)
small_font = ImageFont.truetype('./simsun.ttc', size=10)
font = ImageFont.truetype('./simsun.ttc', size=16)
big_font = ImageFont.truetype('./simsun.ttc', size=32)
img.paste(bg_img, (0,0))
img.paste(weather_img, (5,5), mask=a)

# draw.text((75,5), "周四", font=font, fill="#FFFFFF")
draw.text((80,10), "晴", font=font, fill="#FFFFFF")
draw.text((65,30), "13～28", font=font, fill="#FFFFFF")
# draw.text((65,20), "28", font=big_font, fill="#FFFFFF")
# draw.text((100,25), "℃", font=small_font, fill="#FFFFFF")
draw.text((5,62), "48,良", font=font, fill="#FFFFFF")
# draw.text((,5), "28℃", font=font, fill="#FFFFFF")
# draw.text((0,78), "2019-03-28", font=font, fill="#FFFFFF")

img.show()
