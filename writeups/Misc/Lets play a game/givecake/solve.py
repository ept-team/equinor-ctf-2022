#!/usr/bin/env python3

from PIL import Image
from io import BytesIO
from base64 import b64decode
from collections import defaultdict
import pwn
import sys

COLOR = {
    (255,255,0): "yellow",
    (125,0,125): "purple",
    (128,0,128): "purple",
    (255,0,0): "red",
    (0,128,0): "green",
    (0,0,255): "blue",
    (255,255,255): "white",
    (165,42,42): "brown",
}

def chopchop(im):
    return ({
        "nw": im.crop((0,0, 256,256)),
        "ne": im.crop((256,0, 512,256)),
        "sw": im.crop((0,256, 256,512)),
        "se": im.crop((256,256, 512,512))
    })

def first_color(im):
    "Identify first colored pixel"
    x = 0; y = 0
    while True:
        if x >= 255: 
            x = 0
            y += 1
        if im.getpixel((x,y)) == (0,0,0):
            x += 1
            continue
        else:
            return(x,y)

def identify_part(im):
    threshold = 75
    (x, y) = first_color(im)
    a = count_yellow_on_line(im, y)
    b = count_yellow_on_line(im, y+1)    
    pct = int((a/b)*100)
    if a == 1: return "triangle"
    elif a == b: return "rectangle"
    elif pct < threshold: return "circle"
    return "hexagon"

def count_yellow_on_line(im, y):
    found = 0
    for i in range(0, 256):
        if im.getpixel((i, y)) != (0, 0, 0):
            found += 1
    return found

def identify_color(im):
    for pixel in im.getdata():
        if pixel != (0,0,0):
            return COLOR[pixel]

def identify_image(im):
    out = defaultdict(dict)
    chop = chopchop(im)
    for direction in chop.keys():
        shape = identify_part(chop[direction])
        color = identify_color(chop[direction])
        out[shape][color] = direction
    return out

def get_task(r):
    global level
    try:
        raw = r.recvuntil(b'])?\n').decode("utf-8")
    except:
        pwn.log.success(r.recvall())
        sys.exit()
    pwn.log.info(raw)
    if raw.find("LEVEL")>-1:
        pwn.log.success("Ny level!")
        level += 1
        raw = raw.split("\n")[1]
    if level == 1:
        task = raw.split()[3]
        color = "yellow"
    else:
        color = raw.split()[3]
        task = raw.split()[4]
    pwn.log.info("Task: {} {}".format(color, task))
    return (color, task)

r = pwn.remote('io.ept.gg', '30047')
r.recvuntil(b'ready?\n')
r.sendline()
level = 1
while True:
    (task_color, task_shape) = get_task(r)
    text = r.recvline()
    img = Image.open(BytesIO(b64decode(text)))
    identified = identify_image(img)[task_shape][task_color]
    r.sendline(identified)
    pwn.log.info(r.recvline())
