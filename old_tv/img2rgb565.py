# -*- coding: utf-8 -*-
"""Utility to convert images to raw RGB565 format."""

from PIL import Image
from struct import pack
from os import path
import sys
    
def error(msg):
    """Display error and exit."""
    print (msg)
    sys.exit(-1)

def write_bin(f, pixel_list):
    """Save image in RGB565 format."""
    for pix in pixel_list:
        r = (pix[0] >> 3) & 0x1F
        g = (pix[1] >> 2) & 0x3F
        b = (pix[2] >> 3) & 0x1F
        f.write(pack('>H', (r << 11) + (g << 5) + b))

def convert(in_path, out_path):
    img = Image.open(in_path).convert('RGB')
    pixels = list(img.getdata()) 
    with open(out_path, 'wb') as f:
        write_bin(f, pixels)


if __name__ == "__main__":
    # for i in range(1,25):
        # file_name = "{}.png".format(i)
        # convert(file_name, '{}.raw'.format(file_name))
    file_name = "timg128x96.jpeg"
    convert(file_name, 'timg128x96.raw'.format(file_name))

