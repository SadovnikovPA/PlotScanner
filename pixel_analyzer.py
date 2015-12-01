__author__ = 'Siarshai'

from utils_general import fill_the_gaps

class PixelAnalyzer :

    def __init__(self, a_since_last_threshold, a_max_afterglow):
        self.since_last_threshold = a_since_last_threshold
        self.since_last = self.since_last_threshold
        self.max_afterglow = a_max_afterglow
        self.afterglow = 0
        self.result = 0

    def invalidate(self):
        self.since_last = self.since_last_threshold
        self.afterglow = 0
        self.result = 0

    def consume(self, pixel):
        """
        Marks pixel as border if there were no borders recently and pixel's luminosity > 0
        :param pixel:
        :return:
        """
        self.result = 0
        if pixel > 0:
            if self.afterglow > 0:
                self.result = 255
                self.afterglow -= 1
            elif self.since_last >= self.since_last_threshold:
                self.result = 255
                self.afterglow = self.max_afterglow
            self.since_last = 0
        else:
            self.afterglow = 0
            self.since_last += 1
        return self.result



def mark_external_borders(external_borders_map, gradient_abs_list, y_lo, y_hi, x_lo, x_hi, pa_since_last_threshold, pa_afterglow, should_clear_external_borders_map):
    """
    Applies pixel analyzers to image in 4 main directions marking external borders
    :param external_borders_map: data buffer with already found borders
    :param gradient_abs_list: data buffer with gradient's absolute value
    :param y_lo:
    :param y_hi:
    :param x_lo:
    :param x_hi:
    :param pa_since_last_threshold:
    :param pa_afterglow:
    :param should_clear_external_borders_map:
    :return: modified external borders map
    """

    pixel_analyzer = PixelAnalyzer(pa_since_last_threshold, pa_afterglow)

    if should_clear_external_borders_map:
        for y in range(y_lo, y_hi):
            for x in range(x_lo, x_hi):
                external_borders_map[x, y] = 0

    for y in range(y_lo, y_hi):
        pixel_analyzer.invalidate()
        for x in range(x_lo, x_hi):
            external_borders_map[x, y] = pixel_analyzer.consume(gradient_abs_list[x, y]) if external_borders_map[x, y] == 0 else external_borders_map[x, y]

    for y in range(y_lo, y_hi):
        pixel_analyzer.invalidate()
        for x in range(x_hi - 1, x_lo, -1):
            external_borders_map[x, y] = pixel_analyzer.consume(gradient_abs_list[x, y]) if external_borders_map[x, y] == 0 else external_borders_map[x, y]

    for x in range(x_lo, x_hi):
        pixel_analyzer.invalidate()
        for y in range(y_lo, y_hi):
            external_borders_map[x, y] = pixel_analyzer.consume(gradient_abs_list[x, y]) if external_borders_map[x, y] == 0 else external_borders_map[x, y]

    for x in range(x_lo, x_hi):
        pixel_analyzer.invalidate()
        for y in range(y_hi-1, y_lo, -1):
            external_borders_map[x, y] = pixel_analyzer.consume(gradient_abs_list[x, y]) if external_borders_map[x, y] == 0 else external_borders_map[x, y]

    # Additionally removes stray specks
    external_borders_map = fill_the_gaps(external_borders_map, x_lo, x_hi, y_lo, y_hi)
    external_borders_map = fill_the_gaps(external_borders_map, x_lo, x_hi, y_lo, y_hi)
    external_borders_map = fill_the_gaps(external_borders_map, x_lo, x_hi, y_lo, y_hi)
    return external_borders_map
