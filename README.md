# Tiny TRS-80 Model III Emulation Library

The Tiny TRS-80 Model III, made by Trevor Flowers, is a 1:6 scale model of the classic microcomputer that includes a microcontroller and a 1.69" diagonal display.
See [https://transmutable.com/work/electronic-tiny-trs-80-model-iii](https://transmutable.com/work/electronic-tiny-trs-80-model-iii)

This library provides runtime support in CircuitPython for scale accurate character and graphics rendering on the Tiny TRS-80 Model III's display as well as limited keyboard input over a USB serial connection.

The runtime uses the Kreative Korp TRS-80 Model III fonts [https://www.kreativekorp.com/software/fonts/trs80/](https://www.kreativekorp.com/software/fonts/trs80/), supporting both the 64 character by 16 line and 32 character by 16 line modes.

Also included is a modified version of PyBasic [https://github.com/richpl/PyBasic](https://github.com/richpl/PyBasic) with added support for TRS-80 BASIC display statements and functions.

Finally, the runtime library has been ported to run over PySDL [https://pysdl2.readthedocs.io](https://pysdl2.readthedocs.io) on a regular Python installation for testing.

Read more about this work here [http://www.grwster.com/projects/2024/tinymodel3/](http://www.grwster.com/projects/2024/tinymodel3/)

## Running on a Tiny TRS-80 Model III (CircuitPython)

Plug the Tiny TRS-80 Model III into your computer's USB port, mounting its file system

Install the libraries:

* Copy the Adafruit Bitmap Font library [Adafruit_CircuitPython_Bitmap_Font](https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font/) to the lib dir

* Copy src/lib/tinymodel3.py to the lib dir

* Copy pybasic/lib/tinymodel3_pybasic to the lib dir

Run the updated version of Trevor Flower's default code in 32 or 64 char mode:

* Copy src/default32-code.py or src/default64-code.py to code.py in the top-level dir

Run the python demos:

* Copy src/demos-code.py to code.py in the top-level dir

Run the BASIC demos:

* Copy src/*.bas to the the top-level dir

* Copy basicdemos-code.py to code.py in the top-level dir

## Running on a Mac (should also work on Linux or Windows, but you're on your own)

You'll need Python 3 [https://www.python.org](https://www.python.org) and PySDL [https://pysdl2.readthedocs.io](https://pysdl2.readthedocs.io) installed on your computer

Run the python demos:
```
% cd src
% ./run.sh demos-code.py
```

Run the BASIC demos:
```
% cd src
% ./run.sh basicdemos-code.py
```

Run a single BASIC program:
```
% cd src
% ./runbas.sh demo1.bas
```

## Requirements

In addition to the Adafruit CircuitPython libraries pre-installed by Trevor Flowers on the Tiny Model III, you'll need to install the Adafruit Bitmap Font library:

* [Adafruit_CircuitPython_Bitmap_Font](https://github.com/adafruit/Adafruit_CircuitPython_Bitmap_Font/)

For testing on Mac / Linux / Windows, Python 3 and PySDL are required:

* [https://www.python.org](https://www.python.org)
* [https://pysdl2.readthedocs.io](https://pysdl2.readthedocs.io)
