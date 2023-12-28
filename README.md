# Installation
- You only need the ``main.py`` if you only want to display the colors chosen by the script
- If you want to use nanoleaf you only need ``main.py``, ``getnanoIDs.py`` and ``nanoleaf.py``, and also ``getnanoAuth.py`` if you don't have your nanoleaf auth token.
- ``config.json`` is only needed if you run the script directly and not through a command. Only the "use_nanoleaf" and "show_visual" fields work currently [TODO].
- you need to make an ``auth.json`` file with this structure:
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
- After saving the files you need into a directory, you can run the script using this command in that directory:
  ``py main.py nl gui``
  assuming you have python installed, and you want to use both nanoleaf and the visual graphic. Otherwise, ``nl`` and/or ``gui`` can be omitted.
- If you want to run the command from anywhere, you can either create a .bat file (not covered here) or make a powershell command:
- open powershell
- run ``notepad $PROFILE``
- paste in this:
```
function nlmirror {
   param(
       [string]$arg1 = "",  # Default value for the first argument
       [string]$arg2 = ""  # Default value for the second argument
   )
   C:\path\to\your\python.exe C:\path\to\your\main.py $arg1 $arg2
}
```
- replace the paths with your ``python.exe`` and the ``main.py`` for the project
- you can change the default value if you want
- you can also pick whatever function name you want
- then you can run this command in powershell by typing for example ``nlmirror nl gui``

# Errors
[TODO]
