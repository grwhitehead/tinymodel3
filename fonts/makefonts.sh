
# TRS-80 fonts for use in CircuitPython on the Tiny Model III
#
# 1) Download the TRS-80 fonts from here and unpack them in this directory
# https://www.kreativekorp.com/software/fonts/trs80/
#
# The TRS-80 Model III had two video modes and there's a font for each
#
#   64 chars by 16 lines (default)
#   -> AnotherMansTreasureMIII64C.ttf
#
#   32 chars by 16 lines (accessed by typing SHIFT -> on the keyboard or printing CHR$(23) in software)
#   -> AnotherMansTreasureMIII32C.ttf
#
# 2) To use these true type fonts (ttf) on the Tiny Model III they need to be converted to bitmap fonts (bdf or pcf)
# https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display
#
# This script uses otf2bdf to convert ttf to bdf
# https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display/use-otf2bdf
#
# The Tiny Model III display is 280x240 at 220ppi (1.27"x1.09", 1.69" diagonal)
#
# In 64 char mode we have 280/64 = 4.375 pixels per char
# at 4 pixels per char we'll use 4*64 = 256 pixels and have a margin of 12 pixels on each side of the screen
# the font is barely legible at this resolution, but it gives us a scale accurate rendering
#
# Using otf2bdf to generate the bitmap font we specify a point size of 4 at a resolution of 220 ppi
#
# The Model III character ROM is at code points 0xE000-0xE17F, so we can save space by extracting just
# those characters
#
# On a mac you can install otf2bdf with
# % brew install otf2bdf

# otf2bdf AnotherMansTreasureMIII64C.ttf -p 4 -r 220 -o AnotherMansTreasureMIII64C.bdf
otf2bdf AnotherMansTreasureMIII64C.ttf -l 57344_57727 -p 4 -r 220 -o AnotherMansTreasureMIII64C.bdf

#
# The 32 char mode font renders twice as wide as the 64 char mode font using the same parameters

#otf2bdf AnotherMansTreasureMIII32C.ttf -p 4 -r 220 -o AnotherMansTreasureMIII32C.bdf
otf2bdf AnotherMansTreasureMIII32C.ttf -l 57344_57727 -p 4 -r 220 -o AnotherMansTreasureMIII32C.bdf

#
# 3) You can use the bdf files on the Tiny Model III, but performance is improved by converting them to pcf
# https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display/convert-to-pcf
#
# You can do that here https://adafruit.github.io/web-bdftopcf/ or you can use bdftopcf
#
# On a mac you can install bdftopcf with
# % brew install bdftopcf

bdftopcf AnotherMansTreasureMIII64C.bdf -o AnotherMansTreasureMIII64C.pcf
bdftopcf AnotherMansTreasureMIII32C.bdf -o AnotherMansTreasureMIII32C.pcf

#
# 4) Copy the bitmap fonts into the src tree for deployment on the Tiny Model III

cp AnotherMansTreasureMIII64C.pcf ../src/fonts
cp AnotherMansTreasureMIII32C.pcf ../src/fonts
