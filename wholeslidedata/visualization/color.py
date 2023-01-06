def get_color(annotation, color_map=None):
    color = "black"
    if color_map is not None:
        try:
            color = color_map[annotation.label.name]
        except KeyError:
            try:
                color = color_map[annotation.label.value]
            except KeyError:
                raise KeyError(
                    "Color map is specified for name of value is not defined"
                )
    else:
        try:
            color = annotation.color
        except AttributeError:
            try:
                color = annotation.label.color
            except AttributeError:
                pass
    return color