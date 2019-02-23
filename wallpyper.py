#! /usr/bin/python
import os
import os.path
import random
import subprocess
import struct
import imghdr

#http://stackoverflow.com/questions/3129322/how-do-i-get-monitor-resolution-in-python/31171430#31171430
#pip install screeninfo
from screeninfo import get_monitors

logfile = os.path.expanduser('~')+"/.wallpyer"
wallpaperPaths = os.path.expanduser('~')+'/shinobooru/yande.re', os.path.expanduser('~')+'/shinobooru/konachan.com'

#http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0) # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height

def writeLog(loglist):
    log = open(logfile, 'w')
    for entry in loglist:
        log.write(str(entry)+'\n')

def pickWallpaper(wallpapers, recent, screenRatio):
    wallpaper = None
    while True:
        rndNr = str(random.randrange(len(wallpapers)))
        if str(rndNr) not in recent:
            wallpaper = wallpapers[int(rndNr)]
            imgSize = get_image_size(wallpaper)
            if (imgSize is not None):
                imgRatio = float(imgSize[0])/imgSize[1]
                if (screenRatio < 1 and imgRatio < 1 or screenRatio > 1 and imgRatio > 1):
                    recent.append(rndNr)
                    break
    return wallpaper

def getWallpaperList():
    wallpapers = []
    for path in wallpaperPaths:
        files = os.listdir(path)
        wallpapers += [path+"/"+wallpaper for wallpaper in files]
    return wallpapers

def getRecentWallpaperList(numberOfRecentWallpapers):
    if not os.path.isfile(logfile):
        open(logfile, 'a').close()
        recent = []
    else:
        log = open(logfile, 'r')
        recent = [line.rstrip('\n') for line in log][-numberOfRecentWallpapers:]
        log.close()
    return recent

def callFeh(wallpaperList, recentWallpaperList):
    screens = get_monitors()

    fehcall = ["feh", "--bg-max"]
    paintedScreens = []
    for s in screens:
        #check for overlapping screens
        if not [sc for sc in paintedScreens if sc.x == s.x and sc.y == s.y]:
            screenRatio = float(s.width)/s.height
            pick = pickWallpaper(wallpaperList, recentWallpaperList, screenRatio)
            fehcall.append(pick)
            paintedScreens.append(s)

    subprocess.call(fehcall)

wallpaperList = getWallpaperList()
recentWallpaperList = getRecentWallpaperList(int(len(wallpaperList)*0.5))
callFeh(wallpaperList, recentWallpaperList)
writeLog(recentWallpaperList)

