# wallpyper
Wallpaper changer for linux.

Made to run as a cron job. (command = 'DISPLAY=:0.0 /usr/bin/python \<path to script\>')

Uses screeninfo to get the resolution of the connected monitors, 
select a random image that has a matching aspect ratio(landscape or portrait)
and set a different wallpaper for each screen with feh.

# Dependencies
[screeninfo](https://github.com/rr-/screeninfo) via 'pip install screeninfo'

[feh](https://github.com/derf/feh) via your favorite package manager
