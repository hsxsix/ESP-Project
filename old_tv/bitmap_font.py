"""XGLCD Font Utility."""
from math import floor


class BitmapFont(object):
    """Font data in X-GLCD format.

    Attributes:
        letters: A bytearray of letters (columns consist of bytes)
        width: Maximum pixel width of font
        height: Pixel height of font
        start_letter: ASCII number of first letter
        height_bytes: How many bytes comprises letter height

    Note:
        Font files can be generated with the free version of MikroElektronika
        GLCD Font Creator:  www.mikroe.com/glcd-font-creator
        The font file must be in X-GLCD 'C' format.
        To save text files from this font creator program in Win7 or higher
        you must use XP compatibility mode or you can just use the clipboard.
    """

    # Dict to tranlate bitwise values to byte position
    BIT_POS = {1: 0, 2: 2, 4: 4, 8: 6, 16: 8, 32: 10, 64: 12, 128: 14, 256: 16}

    def __init__(self, bitmap, width, height, letter_count=1):
        """Constructor for X-GLCD Font object.

        Args:
            path (string): Full path of font file
            width (int): Maximum width in pixels of each letter
            height (int): Height in pixels of each letter
            start_letter (int): First ACII letter.  Default is 32.
            letter_count (int): Total number of letters.  Default is 96.
        """
        self.width = width
        self.height = height
        self.letter_count = letter_count
        self.bytes_per_letter = (floor(
            (self.height - 1) / 8) + 1) * self.width  #+ 1
        self.letters = bytearray(self.bytes_per_letter * self.letter_count)
        self.__load_xglcd_font(bitmap)

    def __load_xglcd_font(self, bitmap):
        """Load X-GLCD font data from text file.

        Args:
            path (string): Full path of font file.
        """
        bytes_per_letter = self.bytes_per_letter
        # Buffer to hold letter byte values
        self.letters = bytearray(bytes_per_letter * self.letter_count)
        mv = memoryview(self.letters)
        offset = 0
        # Convert hex strings to bytearray and insert in to letters
        mv[offset: offset + bytes_per_letter] = bytearray(
            int(b, 16) for b in bitmap.split(','))


    def lit_bits(self, n):
        """Return positions of 1 bits only."""
        while n:
            b = n & (~n+1)
            yield self.BIT_POS[b]
            n ^= b

    def get_buf(self, color, background=0, landscape=False):
        """Convert letter byte data to pixels.

        Args:
            letter (string): Letter to return (must exist within font).
            color (int): RGB565 color value.
            background (int): RGB565 background color (default: black).
            landscape (bool): Orientation (default: False = portrait)
        Returns:
            (bytearray): Pixel data.
            (int, int): Letter width and height.
        """
        # Get index of letter
        mv = memoryview(self.letters)

        # Get width of letter (specified by first byte)
        letter_width = mv[0]
        # letter_width = self.width
        letter_height = self.height
        # Get size in bytes of specified letter
        letter_size = letter_height * letter_width
        # Create buffer (double size to accommodate 16 bit colors)
        if background:
            buf = bytearray(background.to_bytes(2, 'big') * letter_size)
        else:
            buf = bytearray(letter_size * 2)

        msb, lsb = color.to_bytes(2, 'big')

        if landscape:
            # Populate in flip order for landscape
            pos = (letter_size * 2) - (letter_height * 2)
        else:
            # Populate buffer in order for portrait
            pos = 0

        lh = letter_height
        # Loop through letter byte data and convert to pixel data
        for b in mv[1:]:
            # Process only colored bits
            for bit in self.lit_bits(b):
                buf[bit + pos] = msb
                buf[bit + pos + 1] = lsb
            if lh > 8:
                # Increment position by double byte
                pos += 16
                lh -= 8
            else:
                if landscape:
                    # Descrease position to start of previous column
                    pos -= (letter_height * 4) - (lh * 2)
                else:
                    # Increase position by remaing letter height to next column
                    pos += lh * 2
            lh = letter_height
        return buf, letter_width, letter_height
