from bitmap_font import BitmapFont

def color565(r, g, b):
    """Return RGB565 color value.

    Args:
        r (int): Red value.
        g (int): Green value.
        b (int): Blue value.
    """
    return (r & 0xf8) << 8 | (g & 0xfc) << 3 | b >> 3

ni  = "0x10,0x00,0x11,0xFC,0x10,0x04,0x10,0x08,0xFC,0x10,0x24,0x20,0x24,0x24,0x27,0xFE,0x24,0x20,0x44,0x20,0x28,0x20,0x10,0x20,0x28,0x20,0x44,0x20,0x84,0xA0,0x00,0x40"

color = color565(100,100,100)
arcadepix = BitmapFont(ni, 16, 16)
buf, w, h = arcadepix.get_buf(color)
print(w,h,buf)

# arcadepix = XglcdFont('', 9, 11)
# buf, w, h = arcadepix.get_letter('A',color)
# print(w,h,buf)