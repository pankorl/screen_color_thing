from nanoleaf_udp import set_individual_panel_colors, nl
from getnanoIDs import get_panel_ids

def color_set_event_handler(devicetype: str, id_colors: dict, transition_time: int =None):
    """
    Gets called when a color is to be set.
    :param id_colors: dict with panel ids and hex colors.
    :param transition_time:
    """


    # For nanoleaf with udp:
    if "nanoleaf" in devicetype:
        set_individual_panel_colors(id_colors, transition_time, fade=False if transition_time == None else transition_time)

def init_event_handler(devicetype: str):
    """
    Gets called once when the script starts.
    """

    # For nanoleaf with udp:
    if "nanoleaf" in devicetype:
        nanoleaf_init_event_handler()


def get_ids(devicetype: str):
    """
    Gets called once when the script starts.
    Only needs to return an iterable of the same length as the number of colors.
    """
    # In hindsight the panel ids aren't really needed in the main script as all the main script uses them for is as keys for the colors.

    # For nanoleaf:
    if "nanoleaf" in devicetype:
        return get_panel_ids()
    

def inc_brightness(devicetype: str):
    
    if "nanoleaf" in devicetype:
        nl.increment_brightness(10)


def set_brightness(devicetype: str, value):
    """
    Set brightness to value in percent
    """

    if "nanoleaf" in devicetype:
        # This isn't over UDP
        nl.set_brightness(value)

def decr_brightness(devicetype: str):
    
    if "nanoleaf" in devicetype:
        nl.increment_brightness(-10)


def nanoleaf_init_event_handler():
    if nl.enable_extcontrol():
        print("extcontrol enabled")
    else:
        print("extcontrol failed")