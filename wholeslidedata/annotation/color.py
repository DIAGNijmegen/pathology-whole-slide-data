
from typing import Union

HEX_TO_COLOR_NAMES = {
    "#000000": "black",
    "#FFFFFF": "white",
    "#FF0000": "red",
    "#00FF00": "green",
    "#0000FF": "blue",
    "#FFFF00": "yellow",
    "#00FFFF": "cyan",
    "#FF00FF": "magenta",
    "#808080": "gray",
    "#800000": "maroon",
    "#008000": "olive",
    "#000080": "navy",
    "#808000": "purple",
    "#800080": "teal",
    "#008080": "aqua",
}
COLOR_NAMES_TO_HEX = {v: k for k, v in HEX_TO_COLOR_NAMES.items()}

class Color:

    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb_color):
        return "#{:02x}{:02x}{:02x}".format(*rgb_color)


    def __init__(self, color: Union[str, tuple]):
        self._hex_color = self._get_hex_color(color)
        self._rgb_color = self._get_rgb_color(color)

    def _get_hex_color(self, color):
        if isinstance(color, str):
            if color[0] != "#":
                color = COLOR_NAMES_TO_HEX[color]
            return color
        return Color.rgb_to_hex(color)
    
    def _get_rgb_color(self, color):
        if isinstance(color, str):
            if color[0] != "#":
                color = COLOR_NAMES_TO_HEX[color]
            return Color.hex_to_rgb(COLOR_NAMES_TO_HEX[color])
        return color
                    

    @property
    def color_name(self):
        return HEX_TO_COLOR_NAMES.get(self.hex_color, 'NA'),
    
    @property
    def rgb_color(self):
        return self._rgb_color

    @property
    def hex_color(self):
        return self._hex_color
