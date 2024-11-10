#
# Tiny TRS-80 Model III Emulation Library
#
# The Tiny TRS-80 Model III is a 1:6 scale model of the classic microcomputer made by Trevor Flowers
# https://transmutable.com/work/electronic-tiny-trs-80-model-iii
#
# This library provides scale accurate character and graphics rendering on the Tiny TRS-80 Model III's
# display. Some day I might add a TRS-80 BASIC interpreter.
#
# MIT License
# 
# Copyright (c) 2024 Greg Whitehead
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import board
import displayio
from adafruit_st7789 import ST7789
import bitmaptools
from adafruit_bitmap_font import bitmap_font
import sys
import time
import supervisor

__runtime = None

def initRuntime(mode=64):
    global __runtime
    assert __runtime is None
    __runtime = Runtime(mode=mode)
    
def getRuntime():
    global __runtime
    if not __runtime:
        initRuntime()
    return __runtime

#
# Runtime class emulating the TRS-80 Model III display at 1:6 scale
#
# The TRS-80 Model III had two video modes, each with it's own font (see makefonts.sh)
#   64 chars by 16 lines (default)
#   32 chars by 16 lines (accessed by typing SHIFT -> on the keyboard or printing CHR$(23) in software)
#
# The Tiny Model III display is 280x240 at 220ppi (1.27"x1.09", 1.69" diagonal)
#
# In 64 char mode we have room for 280/64 = 4.375 pixels per char
# at 4 pixels per char we'll use 4*64 = 256 pixels and have a margin of 12 pixels on each side of the screen
# the chars have a 2:3 aspect ratio, making them 12 pixels high at this scale, so we'll use 12*16 = 192 pixels
# and have a margin of 24 pixels at the top and bottom of the screen
#
# In 32 char mode the characters are twice as wide at the same height
#
# NOTE: When switching to 32 char mode from 64 char mode on a real TRS-80 Model III the screen memory
# remains 1024 characters, but only every other character is rendered (garbling anything on the display
# when switching). Mode switching is not currently supported in this class and instantiating a 32 char
# mode Runtime give you contiguous 512 character screen addressing.
#
# Graphics on the TRS-80 are implemented with characters 0x80 to 0xBF, with the lower six bits mapping to a
# 2x3 grid of rectangular pixels on screen
#
#   -----
#   |0|1|
#   -----
#   |2|3|
#   -----
#   |4|6|
#   -----
#
# In 64 char mode the screen has 128 by 48 pixels, and in 32 char mode it has 64 by 48 pixels
#

class Runtime:
    def __init__(self, mode=64) -> None:
        
        self.display_width = 280
        self.display_height = 240

        self.background_color = 0x111111
        self.font_color = 0xC9CADD
        
        if mode == 64:
            self.line_width = 64
            self.line_count = 16
            self.char_width = 4
            self.char_height = 12
            self.char_descent = 5
            self.font = bitmap_font.load_font("fonts/AnotherMansTreasureMIII64C.pcf")
        elif mode == 32:
            self.line_width = 32
            self.line_count = 16
            self.char_width = 8
            self.char_height = 12
            self.char_descent = 5
            self.font = bitmap_font.load_font("fonts/AnotherMansTreasureMIII32C.pcf")
        else:
            raise ValueError("unsupported mode")

        self.top_margin = int((self.display_height - self.line_count*self.char_height)/2)
        self.left_margin = int((self.display_width - self.line_width*self.char_width)/2)

        displayio.release_displays()
        spi = board.SPI()
        tft_cs = board.D5
        tft_dc = board.D16
        display_bus = displayio.FourWire(
            spi, command=tft_dc, chip_select=tft_cs, reset=board.D9
        )
        display = ST7789(display_bus, width=280, height=240, rowstart=20, rotation=270)

        display_group = displayio.Group()

        self.background_bitmap = displayio.Bitmap(self.display_width, self.display_height, 1)
        self.background_palette = displayio.Palette(1)
        self.background_palette[0] = self.background_color
        self.background_tilegrid = displayio.TileGrid(self.background_bitmap, pixel_shader=self.background_palette, x=0, y=0)
        display_group.append(self.background_tilegrid)
        
        self.chars_bitmap = displayio.Bitmap(self.line_width*self.char_width, self.line_count*self.char_height, 1)
        self.chars_palette = displayio.Palette(2)
        self.chars_palette[0] = 0
        self.chars_palette.make_transparent(0)
        self.chars_palette[1] = self.font_color
        self.chars_tilegrid = displayio.TileGrid(self.chars_bitmap, pixel_shader=self.chars_palette, x=self.left_margin, y=self.top_margin)
        display_group.append(self.chars_tilegrid)

        display.show(display_group)

        # characters displayed on screen
        self.chars_len = self.line_width*self.line_count
        self.chars = [32 for i in range(self.chars_len)]

        # cursor position
        self.cursor = 0

        # hack to simulate typing in demos
        # assign a string to demoInput before calling _input() and the characters will appear,
        # as if typed, with a 200ms delay between. null characters will be skipped over, resulting
        # in a longer delay before the next character apepars. _input() returns on a newline.
        self.demoInput = None
        self.demoInputPos = 0

    def _update_char(self, pos, char) -> None:
        assert char >=0 and char < 256
        if self.chars[pos] == char:
            return
        self.chars[pos] = char
        glyph = self.font.get_glyph(0xE000+char)
        assert glyph is not None
        x = (pos%self.line_width)*self.char_width
        y = (int)(pos/self.line_width)*self.char_height
        # clear character cell
        bitmaptools.fill_region(self.chars_bitmap, x, y, x+self.char_width, y+self.char_height, 0)
        # write new glyph
        x_off = glyph.dx
        y_off = -self.char_descent + self.char_height - glyph.height - glyph.dy
        assert (x + x_off) >= 0 and (x + x_off) < self.line_width*self.char_width
        assert (y + y_off) >= 0 and (y + y_off) < self.line_count*self.char_height
        self._blit(
            self.chars_bitmap,
            x + x_off,
            y + y_off,
            glyph.bitmap,
            x_1=glyph.tile_index*glyph.width,
            y_1=0,
            x_2=glyph.tile_index*glyph.width + glyph.width,
            y_2=glyph.height,
            skip_index=0
        )

    def _scroll(self) -> None:
        #self.chars = self.chars[self.line_width:] + [0 for i in range(self.line_width)]
        for i in range(self.chars_len-self.line_width):
            self.chars[i] = self.chars[i+self.line_width]
        for i in range(self.chars_len-self.line_width,self.chars_len):
            self.chars[i] = 32
        self._blit(
            self.chars_bitmap,
            0,
            0,
            self.chars_bitmap,
            x_1=0,
            y_1=self.char_height,
            x_2=self.line_width*self.char_width,
            y_2=self.line_count*self.char_height,
            skip_index=None
        )
        bitmaptools.fill_region(self.chars_bitmap, 0, (self.line_count-1)*self.char_height, self.line_width*self.char_width, self.line_count*self.char_height, 0)

    def _cls(self) -> None:
        self.chars_bitmap.fill(0)
        #self.chars = [0 for i in range(self.chars_len)]
        for i in range(self.chars_len):
            self.chars[i] = 32
        self.cursor = 0

    def _keep_running(self) -> bool:
        return True

    def _delay(self, ms) -> None:
        time.sleep(ms/1000)

    def _input(self, prompt) -> str:
        if not prompt is None:
            self.print(prompt)
        text = ""
        while True:
            if supervisor.ticks_ms()&0x100 == 0:
                self._update_char(self.cursor, 176)
            else:
                self._update_char(self.cursor, 32)
            if self.demoInput and self.demoInputPos < len(self.demoInput):
                self._delay(200)
                c = self.demoInput[self.demoInputPos]
                #self.demoInputPos += 1
                self.demoInputPos = (self.demoInputPos+1)%len(self.demoInput)
                if ord(c) == 0:
                    continue
                if ord(c) == 10 or ord(c) == 13:
                    self._update_char(self.cursor, 32)
                    break
                text += c
                self._update_char(self.cursor, ord(c))
                self.cursor += 1
            elif supervisor.runtime.serial_bytes_available:
                c = sys.stdin.read(1)
                if ord(c) == 8 or ord(c) == 127:
                    if len(text) > 0:
                        self._update_char(self.cursor, 32)
                        text = text[:-1]
                        self.cursor -= 1
                        self._update_char(self.cursor, 32)
                elif ord(c) == 10 or ord(c) == 13:
                    self._update_char(self.cursor, 32)
                    break
                else:
                    text += c
                    self._update_char(self.cursor, ord(c))
                    self.cursor += 1
        self.print("\n")
        return text


    #
    # Clear the screen
    #
    # TRS-80 BASIC:
    # CLS
    #
    def cls(self) -> None:
        self._cls()

    #
    # Print text starting at current cursor position
    #
    # TRS-80 BASIC:
    # PRINT TEXT$
    #
    def print(self, text) -> None:
        for i in range(len(text)):
            # handle control characters
            c = ord(text[i])
            if c == 8: # 8 BS delete previous char (wraps to end of previous line or end of screen)
                self.cursor = (self.cursor-1+self.chars_len)%self.chars_len
                self._update_char(self.cursor, 32)
            elif c == 10 or c == 13: # 10 LF and 13 CR take cursor to start of next line
                cursor_row = int(self.cursor/self.line_width)
                cursor_col = self.cursor%self.line_width
                # clear remainder of line
                for i in range(self.line_width-cursor_col):
                    self._update_char(self.cursor+i, 32);
                # advance to beginning of next line, scrolling if needed
                if cursor_row < self.line_count-1:
                    cursor_row += 1
                else:
                    self._scroll()
                self.cursor = cursor_row*self.line_width
            elif c == 24: # 24 cursor left takes cursor left (wraps to end of line)
                cursor_row = int(self.cursor/self.line_width)
                cursor_col = self.cursor%self.line_width
                cursor_col = (cursor_col-1+self.line_width)%self.line_width
                self.cursor = cursor_row*self.line_width + cursor_col
            elif c == 25: # 25 cursor right takes cursor right (wraps to beg of line))
                cursor_row = int(self.cursor/self.line_width)
                cursor_col = self.cursor%self.line_width
                cursor_col = (cursor_col+1)%self.line_width
                self.cursor = cursor_row*self.line_width + cursor_col
            elif c == 26: # 26 cursor down takes cursor down (wraps to top of col)
                cursor_row = int(self.cursor/self.line_width)
                cursor_col = self.cursor%self.line_width
                cursor_row = (cursor_row+1)%self.line_count
                self.cursor = cursor_row*self.line_width + cursor_col
            elif c == 27: # 27 cursor up takes cursor up (wraps to bot of col)
                cursor_row = int(self.cursor/self.line_width)
                cursor_col = self.cursor%self.line_width
                cursor_row = (cursor_row-1+self.line_count)%self.line_count
                self.cursor = cursor_row*self.line_width + cursor_col
            elif c == 28: # 28 home takes cursor to 0,0
                self.cursor = 0
            elif c == 29: # 29 sol takes cursor to start of line
                cursor_row = int(self.cursor/self.line_width)
                self.cursor = cursor_row*self.line_width
            elif c == 30: # 30 ceol clears to end of line
                cursor_col = self.cursor%self.line_width
                for i in range(self.line_width-cursor_col):
                    self._update_char(self.cursor+i, 32)
            elif c == 31: # 31 ceof clears to end of screen
                for i in range(self.chars_len-self.cursor):
                    self._update_char(self.cursor+i, 32)
            elif c >= 191 and c < 256: # 191-255 tab to 0-63 (no effect if cursor past that point)
                cursor_row = int(self.cursor/self.line_width)
                cursor_col = self.cursor%self.line_width
                tab_col = c-191
                if cursor_col < tab_col:
                    cursor_col = tab_col
                self.cursor = cursor_row*self.line_width + cursor_col
            else:
                self._update_char(self.cursor, c)
                self.cursor += 1
                if self.cursor >= self.chars_len:
                    self._scroll()
                    self.cursor = (self.line_count-1)*self.line_width
        
    #
    # Print text starting at pos
    #
    # TRS-80 BASIC:
    # PRINT @pos,TEXT$
    #
    def print_at(self, pos, text) -> None:
        assert pos >= 0 and pos < self.line_width*self.line_count
        self.cursor = pos
        self.print(text)

    #
    # Return tab character for Nth tab stop
    #
    # TRS-80 BASIC:
    # TAB(n)
    def tab(self, n) -> str:
        assert n >= 0 and n < 64
        return chr(191+n)

    #
    # Set pixel at x,y on the screen
    #
    # TRS-80 BASIC:
    # SET(x,y)
    #
    def set(self, x, y) -> None:
        assert x >= 0 and x < self.line_width*2
        assert y >= 0 and y < self.line_count*3
        row = (int)(y/3)
        col = (int)(x/2)
        pos = row*self.line_width+col
        b = self.chars[pos]
        if not b&0x80:
            b = 0x80
        b |= 1<<(2*(y%3) + x%2)
        self._update_char(pos, b)

    #
    # Reset pixel at x,y on the screen
    #
    # TRS-80 BASIC:
    # RESET(x,y)
    #
    def reset(self, x, y) -> None:
        assert x >= 0 and x < self.line_width*2
        assert y >= 0 and y < self.line_count*3
        row = (int)(y/3)
        col = (int)(x/2)
        pos = row*self.line_width+col
        b = self.chars[pos]
        if not b&0x80:
            b = 0x80
        b &= 0xFFFF^(1<<(2*(y%3) + x%2))
        self._update_char(pos, b)

    #
    # Get the value of the pixel at x,y on the screen
    #
    # TRS-80 BASIC:
    # POINT(x,y)
    #
    def point(self, x, y) -> bool:
        assert x >= 0 and x < self.line_width*2
        assert y >= 0 and y < self.line_count*3
        row = (int)(y/3)
        col = (int)(x/2)
        pos = row*self.line_width+col
        b = self.chars[pos]
        if not b&0x80:
            return False
        return (b & 1<<(2*(y%3) + x%2)) > 0

    #
    # Get the value of memory at address
    # (only supported for video memory)
    #
    # TRS-80 BASIC:
    # PEEK(addr)
    #
    def peek(self, addr) -> int:
        if addr >= 15360 and addr < 15360+self.chars_len:
            return int(self.chars[addr-15360])
        return 0

    #
    # Set the value of memory at address
    # (only supported for video memory)
    #
    # TRS-80 BASIC:
    # POKE(addr, val)
    #
    def poke(self, addr, val) -> None:
        if addr >= 15360 and addr < 15360+self.chars_len:
            self._update_char(addr-15360, val)

    #
    # Read a line of input from the keyboard
    #
    # TRS-80 BASIC:
    # INPUT "prompt";A$
    # INPUT A$
    #
    def input(self, prompt=None) -> str:
        return self._input(prompt)


    #
    # delay(milliseconds)
    #
    # delay without blocking event processing when running over SDL runtime
    #
    # replace time.sleep(secs) with runtime.delay(1000*secs)
    #
    def delay(self, ms) -> None:
        self._delay(ms)

    #
    # wait()
    #
    # wait for exit without blocking event processing when running over SDL runtime
    #
    # replace
    #
    # while True:
    #     pass
    #
    # with
    #
    # runtime.wait()
    #
    def wait(self) -> None:
        while True:
            pass



    #
    # Copied from adafruit_display_text.bitmap_label (MIT License)
    #
    
    def _blit(
        self,
        bitmap: displayio.Bitmap,  # target bitmap
        x: int,  # target x upper left corner
        y: int,  # target y upper left corner
        source_bitmap: displayio.Bitmap,  # source bitmap
        x_1: int = 0,  # source x start
        y_1: int = 0,  # source y start
        x_2: int = None,  # source x end
        y_2: int = None,  # source y end
        skip_index: int = None,  # palette index that will not be copied
        # (for example: the background color of a glyph)
    ) -> None:
        # pylint: disable=no-self-use, too-many-arguments

        if hasattr(bitmap, "blit"):  # if bitmap has a built-in blit function, call it
            # this function should perform its own input checks
            bitmap.blit(
                x,
                y,
                source_bitmap,
                x1=x_1,
                y1=y_1,
                x2=x_2,
                y2=y_2,
                skip_index=skip_index,
            )
        elif hasattr(bitmaptools, "blit"):
            bitmaptools.blit(
                bitmap,
                source_bitmap,
                x,
                y,
                x1=x_1,
                y1=y_1,
                x2=x_2,
                y2=y_2,
                skip_source_index=skip_index,
            )

        else:  # perform pixel by pixel copy of the bitmap
            # Perform input checks

            if x_2 is None:
                x_2 = source_bitmap.width
            if y_2 is None:
                y_2 = source_bitmap.height

            # Rearrange so that x_1 < x_2 and y1 < y2
            if x_1 > x_2:
                x_1, x_2 = x_2, x_1
            if y_1 > y_2:
                y_1, y_2 = y_2, y_1

            # Ensure that x2 and y2 are within source bitmap size
            x_2 = min(x_2, source_bitmap.width)
            y_2 = min(y_2, source_bitmap.height)

            for y_count in range(y_2 - y_1):
                for x_count in range(x_2 - x_1):
                    x_placement = x + x_count
                    y_placement = y + y_count

                    if (bitmap.width > x_placement >= 0) and (
                        bitmap.height > y_placement >= 0
                    ):  # ensure placement is within target bitmap
                        # get the palette index from the source bitmap
                        this_pixel_color = source_bitmap[
                            y_1
                            + (
                                y_count * source_bitmap.width
                            )  # Direct index into a bitmap array is speedier than [x,y] tuple
                            + x_1
                            + x_count
                        ]

                        if (skip_index is None) or (this_pixel_color != skip_index):
                            bitmap[  # Direct index into a bitmap array is speedier than [x,y] tuple
                                y_placement * bitmap.width + x_placement
                            ] = this_pixel_color
                    elif y_placement > bitmap.height:
                        break
