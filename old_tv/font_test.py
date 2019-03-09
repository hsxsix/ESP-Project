from machine import Pin, SPI
from ssd1351 import Display, color565
from bitmap_font import BitmapFont

s  = "0x10,0x00,0x11,0xFC,0x10,0x04,0x10,0x08,0xFC,0x10,0x24,0x20,0x24,0x24,0x27,0xFE,0x24,0x20,0x44,0x20,0x28,0x20,0x10,0x20,0x28,0x20,0x44,0x20,0x84,0xA0,0x00,0x40"
spi = SPI(2, sck=Pin(18), mosi=Pin(23), miso=Pin(19),baudrate=14500000)
display = Display(spi, dc=Pin(17), cs=Pin(5), rst=Pin(16))

while True:
    s = input("please input:")
    arcadepix = BitmapFont(s, 16, 16)
   
    display.draw_bitmap(32,64,arcadepix, color565(100,100,100))
# buf, w, h = arcadepix.get_buf(color)
# print(w,h,buf)

# arcadepix = XglcdFont('', 9, 11)
# buf, w, h = arcadepix.get_letter('A',color)
# print(w,h,buf)