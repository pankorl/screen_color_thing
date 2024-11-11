# Installation
- clone or download the repo
- Dependencies [TODO]

## For use with Nanoleaf
- you need to make an ``auth.json`` file in the same folder with this structure:
```json
{
    "auth": "yourAuthToken",
    "ip": "yourNanoleafIP"
}
```
  If you don't have an auth token, put the IP address of your nanoleaf into auth.json, hold the power button on your nanoleaf until it starts flashing, and run ``getnanoAuth.py`` to get the auth token.
  If you don't have the IP address, use a free tool like [advanced ip scanner](https://www.advanced-ip-scanner.com/) to scan your network. Look for something that says nanoleaf. If there is no nanoleaf, try pasting the unnamed IPs into your browser (like http://yourIP) until you find the nanoleaf one.
- All files have to be in the same folder

# Use
### Configuration
- The ``config.json`` file contains the default config values. Some of them can be set through parameters when launching the script (see "Running"):
```py
{
    "use_lights": true, # set this to false if you just want the overlay with default_num_colors colors
    "lights_type": "nanoleaf", # change this to change which event handlers are being called in colorset_events.py. (See "Use with other devices")
    "show_visual": true, # set this to false if you don't want to run with the overlay
    "less_sensitive": false, # set this to true if color transitions are too choppy
    "min_color_amnt": 10, # determines how much of a color must be present to be seen by the color picker at all. The total amount of colors on the screen is 1080*0.05*1920*0.05 = 5184.
    "screen_partitions": [], # set this if you want to partition the screen into different parts. format for 4 quadrants is [[[0,0.5],[0,0.5]], [[0,0.5],[0.5,1]], [[0.5,1],[0,0.5]], [[0.5,1],[0.5,1]]]
    "gui_w_h": [20, 120], # width and height of the overlay
    "default_num_colors": 3, # number of colors displayed when use_lights is false
    "transition_time": 5, # transition time sent to color change event handlers
    "quick_change_thresh": 120 # lower threshold for total color distance to instantly change color of panels instead of fading when less_sensitive is false
}
```
### Running
NB! Note that the script must be stopped from the systems tray. Find the nlmirror icon and right click -> Exit.
#### Quick start
- The easiest way to run the script is to launch ``main.py`` after the installation steps (including "For use with Nanoleaf").
#### Use with different parameters
- You can either use the ``config.json`` to set the parameters and then launch ``main.py``, or run the script using this command in the main directory:
  ``py main.py nl gui ls``
  assuming you have python installed, and you want to use both nanoleaf and the visual overlay. Otherwise, ``nl`` and/or ``gui`` can be omitted. ``ls`` will disable instant color change for changes above the ``quick_change_thresh`` threshold. With ``ls`` in the command, colors always change gradually according to ``transition_time``.
#### Running from taskbar
[TODO]
#### Using global powershell command
- If you want to run the command from anywhere, you can either create a .bat file (not covered here) or make a powershell command:
- open powershell
- run ``notepad $PROFILE``
- paste this into the notepad:
```
function nlmirror {
   param(
       [string]$arg1 = "",  # Default value for the first argument
       [string]$arg2 = "",
       [string]$arg3 = ""
   )
   C:\path\to\your\python.exe C:\path\to\your\main.py $arg1 $arg2 $arg3
}
```
- replace the paths with your ``python.exe`` and the ``main.py`` for the project
- change the default values if you want
- pick whatever function name you want
- run this command in powershell by typing for example ``nlmirror nl gui``

### Additional tips
If the Nanoleaf device is controlled by another app, the udp stream shuts off. This is so you can override control by using other apps (e.g. to turn the lights off). The udp stream has to be turned back on for this program to continue. This can be done by **any** of the following ways:
- Set the brightness to 69% (by any means)
- Press reload button in systems tray
- Toggle overlay in systems tray
- Restart program

Only one of the above steps is needed for the program to continue.

# Use with other devices
- All interactions with the nanoleaf goes through ``colorset_events.py``. 
- The handler functions there can be changed to fit with your own script.
- Add your imports and add your own function calls inside the event handler functions.
- Change ``lights_type`` in ``config.json`` to whatever you want to be passed in as the devicetype parameter in the event handlers. You can make this a string containing multiple words to make the script run on multiple types of devices at once, though this may introduce delays as the script runs on a single CPU thread (untested).

# Errors
[TODO]
