import tinymodel3
import random

runtime = tinymodel3.Runtime()

def demo_1():
    # scrolling
    for i in range(32):
        if (i+1) < 10:
            runtime.print(" ")
        runtime.print(str(i+1)+" ")
        runtime.print("."*(64-3))

def demo_2():
    # fill screen
    for y in range(48):
        for x in range(128):
            runtime.set(x,y)
    for y in range(48):
        for x in range(128):
            runtime.reset(x,y)

def demo_3():
    # spiral
    s = 2
    ss = int(24/s)
    for i in range(ss):
        lx = i*s
        uy = i*s
        rx = 127-i*s
        ly = 47-i*s
        for x in range(lx,rx):
            runtime.set(x,uy)
        for y in range(uy,ly):
            runtime.set(rx,y)
        for x in range(rx,lx+s,-1):
            runtime.set(x,ly)
        for y in range(ly,uy+s,-1):
            runtime.set(lx+s,y)
    for i in range(ss):
        lx = i*s
        uy = i*s
        rx = 127-i*s
        ly = 47-i*s
        for x in range(lx,rx):
            runtime.reset(x,uy)
        for y in range(uy,ly):
            runtime.reset(rx,y)
        for x in range(rx,lx+s,-1):
            runtime.reset(x,ly)
        for y in range(ly,uy+s,-1):
            runtime.reset(lx+s,y)
    
def demo_4():
    # radial lines
    for x in range(0,128,8):
        line(64,24,x,0)
    for y in range(0,48,4):
        line(64,24,127,y)
    for x in range(127,-1,-8):
        line(64,24,x,47)
    for y in range(47,-1,-4):
        line(64,24,0,y)

#
# line drawing routine implementing Bresenham's algorithm based on
#
# Line Drawing Routines for the TRS-80 by Richard Wagner and Frederick Wagner
# Creative Computing, July 1983, p142
#
# https://archive.org/details/creativecomputing-1983-07/page/n145/mode/2up
#
def line(x1,y1,x2,y2):
    dx = x2-x1
    dy = y2-y1
    ix = 1
    if dx < 0:
        ix = -1
        dx = -dx
    iy = 1
    if dy < 0:
        iy = -1
        dy = -dy
    if dy > dx:
        ei = 2*dx
        ed = ei - 2*dy
        e = -dy + ei
        for i in range(1,dy+1):
            runtime.set(x1,y1)
            y1 = y1 + iy
            if e < 0:
                e = e + ei
            else:
                x1 = x1 + ix
                e = e + ed
        runtime.set(x1,y1)
    else:
        ei = 2*dy
        ed = ei - 2*dx
        e = -dx + ei
        for i in range(1,dx+1):
            runtime.set(x1,y1)
            x1 = x1 + ix
            if e < 0:
                e = e + ei
            else:
                y1 = y1 + iy
                e = e + ed
        runtime.set(x1,y1)

demos = [
    demo_1,
    demo_2,
    demo_3,
    demo_4
]

while True:
    for demo in demos:
        runtime.cls()
        demo()
        runtime.delay(1000)
