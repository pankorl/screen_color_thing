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
- This all has to be in the same folder

# Use
- After saving the files you need into a directory, you can run the script using this command in that directory:
  ``py main.py nl gui``
  assuming you have python installed, and you want to use both nanoleaf and the visual graphic. Otherwise, ``nl`` and/or ``gui`` can be omitted.

# Errors
[TODO]
