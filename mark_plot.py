__author__ = 'Siarshai'

from math import sqrt

from PIL import ImageDraw
import numpy as np

from find_crosses import find_crosses
import utils_general
from utils_general import convert_image_to_data_buffer
from utils_draw import draw_point_plot


def prepare_poly_interpolated_plot(x_list, y_list, pts_number, f_poly_power=-1):
    if len(x_list) != len(y_list):
        raise ValueError("ERROR: x_list and y_list should have equal length to interpolate")
    if f_poly_power < 1:
        f_poly_power = int(1 + sqrt(len(x_list)))
    if utils_general.is_debug:
        print("Number of x points: {}, poly max degree: {}".format(len(x_list), f_poly_power))
    f_poly_coeffs = np.polyfit(x_list, y_list, f_poly_power)
    f_poly = np.poly1d(f_poly_coeffs)
    xp = np.linspace(x_list[0], x_list[-1], pts_number)
    yp = f_poly(xp)
    return xp, yp


def mark_plot(image, f_poly_power = -1, plot_pts_size=50):
    """
    Searches for plot axes and point marks then constructs a poly to interpolate a diagram
    :param image: image to operate on
    :param f_poly_power: one can specifically set power of interpolation poly
    :param plot_pts_size: number of points in drawn plot
    :return:
    """

    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()

    image_data = convert_image_to_data_buffer(pix, width, height, channels=3)
    x_axis_cross, y_axis_cross, crosses_result_list = find_crosses(image_data)

    #This step is crucial for further poly interpolation and diagram drawing
    crosses_result_list.sort(reverse=True, key=lambda x: x[0])

    x_list = [point[0] for point in crosses_result_list]
    y_list = [point[1] for point in crosses_result_list]

    xp, yp = prepare_poly_interpolated_plot(x_list, y_list, plot_pts_size, f_poly_power)
    draw_point_plot(draw, xp, yp, plot_pts_size)

    draw.point((x_axis_cross, y_axis_cross), (255, 0, 0))
    for pt in crosses_result_list:
        draw.point((pt[0], pt[1]), (0, 255, 0))
