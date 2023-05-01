from bisect import bisect_left


_QUANTIZED_SPACINGS = [(0.125 / 8) * (2 * 2**i) for i in range(16)]


def take_closest_level(spacings, spacing):
    pos = bisect_left(spacings, spacing)
    if pos == 0:
        return pos
    if pos == len(spacings):
        return pos - 1
    if spacings[pos] - spacing < spacing - spacings[pos - 1]:
        return pos
    return pos - 1


def get_quantized_spacing(spacings, spacing):
    return spacings[take_closest_level(spacings, spacing)]


def get_coordinate_spacing(spacing_level_0, spacing, relative):
    if relative is False:
        return get_quantized_spacing(_QUANTIZED_SPACINGS, spacing_level_0)
    if relative is True:
        return get_quantized_spacing(_QUANTIZED_SPACINGS, spacing)
    if type(relative) in (float, int):
        return get_quantized_spacing(_QUANTIZED_SPACINGS, relative)
    raise ValueError(f"relative {relative} is not a valid value")


def calculate_ratios_and_spacings(
    spacings, spacing: float, relative: bool = False
):
    calibrated_spacing = get_quantized_spacing(_QUANTIZED_SPACINGS, spacings[0])
    coordinate_spacing = get_coordinate_spacing(spacings[0], spacing, relative)
    quantized_spacing = get_quantized_spacing(_QUANTIZED_SPACINGS, spacing)
    sample_spacing = get_quantized_spacing(spacings, quantized_spacing)
    quantized_sample_spacing = get_quantized_spacing(
        _QUANTIZED_SPACINGS, sample_spacing
    )

    coordinate_ratio = coordinate_spacing / calibrated_spacing
    sample_ratio = quantized_sample_spacing / calibrated_spacing
    quantize_ratio = quantized_spacing / quantized_sample_spacing

    return coordinate_ratio, sample_ratio, quantize_ratio, quantized_sample_spacing
