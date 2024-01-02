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

    # For nanoleaf:
    if "nanoleaf" in devicetype:
        return get_panel_ids()



def nanoleaf_init_event_handler():
    if nl.enable_extcontrol():
        print("extcontrol enabled")
    else:
        print("extcontrol failed")