__author__ = 'Siarshai'

from math import sin, cos, pi
from os import makedirs
from os.path import exists

import numpy


debug = True


def ensure_path_exists(path):
    if not exists(path):
        makedirs(path)


# def filter_2_ul(gradient_abs_list, width, height, f):
#     """ Applies size 2 filter to memory buffer. Center is upper left pixel
#     :param gradient_abs_list:
#     :param width:
#     :param height:
#     :param f: applied filter
#     :return: modified gradient_abs_list
#     """
#     gradient_abs_list_postmodified = []
#     for x in range(width):
#         tmp_gradient_abs_list_postmodified = []
#         for y in range(height):
#             if x == width - 1 or y == height - 1:
#                 tmp_gradient_abs_list_postmodified.append(0)
#             else:
#                 temp = f(gradient_abs_list[x][y], gradient_abs_list[x+1][y],
#                            gradient_abs_list[x][y+1], gradient_abs_list[x+1][y+1])
#                 tmp_gradient_abs_list_postmodified.append(temp)
#         gradient_abs_list_postmodified.append(tmp_gradient_abs_list_postmodified)
#     return gradient_abs_list_postmodified


def filter_2_dr_list(gradient_abs_list, width, height, f):
    """
    Applies size 2 filter to memory buffer. Center is down right pixel
    :param gradient_abs_list:
    :param width:
    :param height:
    :param f: applied filter
    :return: modified gradient_abs_list
    """
    gradient_abs_list_postmodified = []
    for x in range(width):
        tmp_gradient_abs_list_postmodified = []
        for y in range(height):
            if x == 0 or y == 0:
                tmp_gradient_abs_list_postmodified.append(0)
            else:
                temp = f(gradient_abs_list[x][y], gradient_abs_list[x-1][y],
                           gradient_abs_list[x][y-1], gradient_abs_list[x-1][y-1])
                tmp_gradient_abs_list_postmodified.append(temp)
        gradient_abs_list_postmodified.append(tmp_gradient_abs_list_postmodified)
    return gradient_abs_list_postmodified


def filter_2_ur(data_buffer, width, height, f):
    """
    Applies size 2 filter to memory buffer. Center is down right pixel
    :param gradient_abs_list:
    :param width:
    :param height:
    :param f: applied filter
    :return: modified gradient_abs_list
    """
    for x in range(width):
        for y in range(height):
            if x == width-1 or y == height-1:
                data_buffer[x, y] = 0
            else:
                data_buffer[x, y] = f(data_buffer[x, y], data_buffer[x+1, y],
                           data_buffer[x, y+1], data_buffer[x+1, y+1])


def fill_the_gaps_list(data_buffer_2d, x_lo, x_hi, y_lo, y_hi):
    """
    Deletes sole pixels of color mismatching background
    :param data_buffer_2d:
    :param x_lo:
    :param x_hi:
    :param y_lo:
    :param y_hi:
    :return: modified data_buffer_2d
    """
    modified_list = []
    for x in range(x_lo, x_hi):
        tmp_modified_list = []
        for y in range(y_lo, y_hi):
            if x == x_lo or y == y_lo or x == x_hi - 1 or y == y_hi - 1:
                tmp_modified_list.append(0)
            else:
                temp = data_buffer_2d[x-1][y] + data_buffer_2d[x+1][y] + \
                       data_buffer_2d[x-1][y-1] + data_buffer_2d[x][y-1] + data_buffer_2d[x+1][y-1] + \
                       data_buffer_2d[x-1][y+1] + data_buffer_2d[x][y+1] + data_buffer_2d[x+1][y+1]
                if temp >= 7*255:
                    tmp_modified_list.append(255)
                elif temp <= 255:
                    tmp_modified_list.append(0)
                else:
                    tmp_modified_list.append(data_buffer_2d[x][y])
        modified_list.append(tmp_modified_list)
    return modified_list


def fill_the_gaps(data_buffer, x_lo, x_hi, y_lo, y_hi):
    """
    Deletes sole pixels of color mismatching background
    :param data_buffer_2d:
    :param x_lo:
    :param x_hi:
    :param y_lo:
    :param y_hi:
    :return: modified data_buffer_2d
    """
    modified_data_buffer = numpy.copy(data_buffer)
    for x in range(x_lo, x_hi):
        for y in range(y_lo, y_hi):
            if x == x_lo or y == y_lo or x == x_hi - 1 or y == y_hi - 1:
                modified_data_buffer[x, y] = 0
            else:
                temp = data_buffer[x-1, y] + data_buffer[x+1, y] + \
                       data_buffer[x-1, y-1] + data_buffer[x, y-1] + data_buffer[x+1, y-1] + \
                       data_buffer[x-1, y+1] + data_buffer[x, y+1] + data_buffer[x+1, y+1]
                if temp >= 7*255:
                    modified_data_buffer[x, y] = 255
                elif temp <= 255:
                    modified_data_buffer[x, y] = 0
                else:
                    modified_data_buffer[x, y] = data_buffer[x, y]
    return modified_data_buffer


def unpack_line(line):
    """
    Returns (a, b, rho) parameters of 'a*x + b*y = rho' line from packed (alpha, rho) representation. Alpha gets translated
    from degrees to radians.
    a = sin(alpha)
    b = -cos(alpha)
    rho = rho
    :param line: (alpha, rho)
    :return: (a, b, rho)
    """
    a1 = sin(line[0]*pi/180.0)
    b1 = -cos(line[0]*pi/180.0)
    rho1 = -line[1]
    return a1, b1, rho1


def line_instersection(a1, b1, rho1, a2, b2, rho2):
    """
    Finds intersection of two 'a*x + b*y = rho' lines
    :param a1: line 1 a parameter
    :param b1: line 1 b parameter
    :param rho1: line 1 rho parameter
    :param a2: line 2 a parameter
    :param b2: line 2 b parameter
    :param rho2: line 2 rho parameter
    :return: intersection point
    """
    det0 = a1*b2 - b1*a2
    if det0 == 0:
        if rho1 == rho2:
            raise ValueError("Overlap")
        else:
            raise ValueError("Parallel")
    det1 = rho1*b2 - b1*rho2
    det2 = a1*rho2 - rho1*a2
    x = det1/det0
    y = det2/det0
    return x, y


def dot_product(a1, b1, a2, b2):
    return a1*a2 + b1*b2


def make_axby_line(a, b, rho):
    """
    Constructs function which returns value of line in certain (x, y) point
    :param a: line a parameter
    :param b: line a parameter
    :param rho: line a parameter
    :return: resulting function
    """
    def line(x, y):
        return a*x + b*y + rho
    return line


def make_kx_line(a, b, rho):
    """
    Constructs function y = k*x + b which returns value of line in 'x' point
    :param a: line a parameter
    :param b: line a parameter
    :param rho: line a parameter
    :return: resulting function
    """
    if b == 0:
        b = 0.000001
    def line(x):
        return (rho - a*x)/b
    return line


def make_ky_line(a, b, rho):
    """
    Constructs function x = k*y + b which returns value of line in 'y' point
    :param a: line a parameter
    :param b: line a parameter
    :param rho: line a parameter
    :return: resulting function
    """
    if a == 0:
        a = 0.000001
    def line(y):
        return (rho - b*y)/a
    return line


def make_x0y0_poly2(x1, y1, x2, y2):
    """
    Constructs power-2 poly passing through points (0, 0), (x1, y1) and (x2, y2)
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return: resulting poly
    """
    det0 = x1*x1*x2 - x1*x2*x2
    det1 = y1*x2 - x1*y2
    det2 = x1*x1*y2 - y1*x2*x2
    a = det1/det0
    b = det2/det0
    def poly(x):
        return float(x)*(a*x + b)
    return poly


def make_slope_function(x1, y1, x2, y2):
    """
    Constructs slope function passing through points (x1, y1) and (x2, y2).
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return: resulting slope function
    """
    def slope(x):
        if x < x1:
            return y1
        elif x > x2:
            return y2
        return float(x - x1)/(x2 - x1)*(y2 - y1) + y1
    return slope


colorfulness_poly = make_x0y0_poly2(25, 10, 40, 30)
luminosity_sigma = make_slope_function(140, 0, 170, 0.66)
colorfulness_sigma = make_slope_function(60, 0.66, 100, 0)


def is_white(r, g, b):
    """
    Decides if the pixel is white according to its luminosity and colorfulness
    :param r:
    :param g:
    :param b:
    :return: True if pixel is white
    """
    luminosity = luminosity_sigma( (r + g + b)/3 )
    if luminosity == 0:
        return False
    colorfulness = colorfulness_poly(abs(r - g)) + colorfulness_poly(abs(g - b)) + colorfulness_poly(abs(b - r))
    colorfulness = colorfulness_sigma(colorfulness)
    if colorfulness == 0:
        return False
    return luminosity + colorfulness > 1


def is_local_maximum(data_buffer_2d, x0, y0, width, height, radius):
    """
    Returns true if all pixels in data buffer around given pixel is lesser
    :param data_buffer_2d:
    :param x0:
    :param y0:
    :param width:
    :param height:
    :param radius:
    :return:
    """
    for i in range(-radius, radius):
        for j in range(-radius, radius):
            if i != 0 or j != 0:
                if 0 <= x0 + i < width and 0 <= y0 + j < height:
                    if data_buffer_2d[x0 + i][y0 + j] > data_buffer_2d[x0][y0]:
                        return False
    return True


def is_local_maximum_circular(data_buffer_2d, x0, y0, width, height, width_radius, height_radius):
    """
    Returns true if all pixels in data buffer around given pixel is lesser.
    If area surpasses the border data on the other side of data_buffer_2d is analyzed as continuation.
    :param data_buffer_2d:
    :param x0:
    :param y0:
    :param width:
    :param height:
    :param width_radius:
    :param height_radius:
    :return:
    """
    for i in range(-width_radius, width_radius):
        for j in range(-height_radius, height_radius):
            if i != 0 or j != 0:
                x = (x0 + i)%width
                y = (y0 + j)%height
                if data_buffer_2d[x][y] > data_buffer_2d[x0][y0]:
                    return False
    return True


def map_to_origin_rectangle(ul, ur, dl, dr, thumbnail_factor):
    """
    Maps four corners of rectangle to corresponding corners on original image's rectangle
    :param ul:
    :param ur:
    :param dl:
    :param dr:
    :param thumbnail_factor:
    :return: four points (x, y) representing: upper-left corner, upper-right corner, down-left corner, down-right corner
    """
    ul_orig = [ul[0]*thumbnail_factor + thumbnail_factor, ul[1]*thumbnail_factor]
    ur_orig = [ur[0]*thumbnail_factor, ur[1]*thumbnail_factor]
    dr_orig = [dr[0]*thumbnail_factor + thumbnail_factor, dr[1]*thumbnail_factor]
    dl_orig = [dl[0]*thumbnail_factor + thumbnail_factor, dl[1]*thumbnail_factor + thumbnail_factor]
    return ul_orig, ur_orig, dl_orig, dr_orig


def convert_image_to_data_buffer(pix, width, height, mode=3, orientation=1):
    if orientation == 1:
        if mode == 1:
            return numpy.array([[pix[x, y] for x in range(width)] for y in range(height)])
        else:
            return numpy.array([[(pix[x, y][0] + pix[x, y][1] + pix[x, y][2])/3 for x in range(width)] for y in range(height)])
    else:
        if mode == 1:
            return numpy.array([[pix[x, y] for y in range(height)] for x in range(width)])
        else:
            return numpy.array([[(pix[x, y][0] + pix[x, y][1] + pix[x, y][2])/3 for y in range(height)] for x in range(width)])
