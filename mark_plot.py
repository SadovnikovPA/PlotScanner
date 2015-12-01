from math import sqrt

from PIL import ImageDraw
import numpy as np

from kernels import apply_apply_gaussian_laplasian_to_image
from find_hough_lines import find_crosses
from utils_general import debug, convert_image_to_data_buffer
from utils_draw import draw_point_plot


def prepare_poly_interpolated_plot(x_list, y_list, pts_number, f_poly_power=-1):
    if len(x_list) != len(y_list):
        raise ValueError("ERROR: x_list and y_list should have equal length to interpolate")
    if f_poly_power < 1:
        f_poly_power = int(1 + sqrt(len(x_list)))
    if debug:
        print("Number of x points: {}, poly max degree: {}".format(len(x_list), f_poly_power))
    f_poly_coeffs = np.polyfit(x_list, y_list, f_poly_power)
    f_poly = np.poly1d(f_poly_coeffs)
    xp = np.linspace(x_list[0], x_list[-1], pts_number)
    yp = f_poly(xp)
    return xp, yp


def mark_plot(image, laplasian_threshold = 20, f_poly_power = -1, plot_pts_size=50):
    """
    Searches for plot axes and point marks then constructs a poly to interpolate a diagram
    :param image: image to operate on
    :return:
    """

    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    pix = image.load()

    image_data = convert_image_to_data_buffer(pix, width, height, mode=3)

    #Applies horizontal and vertical gaussian's laplasians
    simple_derivative = np.array([[-1, 1]])
    longitude_kernel = np.array([[0.33], [0.33], [0.33]])
    data_h_laplasian = apply_apply_gaussian_laplasian_to_image(image_data, simple_derivative, longitude_kernel, width, height, image_type = "buffer")
    for x in np.nditer(data_h_laplasian, op_flags=['readwrite']):
         x[...] = x if x > laplasian_threshold else 0

    simple_derivative = np.array([[-1], [1]])
    longitude_kernel = np.array([[0.33, 0.33, 0.33]])
    data_v_laplasian = apply_apply_gaussian_laplasian_to_image(image_data, simple_derivative, longitude_kernel, width, height, image_type = "buffer")
    for x in np.nditer(data_v_laplasian, op_flags=['readwrite']):
         x[...] = x if x > laplasian_threshold else 0

    x_axis_cross, y_axis_cross, crosses_result_list = find_crosses(data_h_laplasian, data_v_laplasian, image_data)


    #This step is crucial for further poly interpolation and diagram drawing
    crosses_result_list.sort(reverse=True, key=lambda x: x[0])

    x_list = [point[0] for point in crosses_result_list]
    y_list = [point[1] for point in crosses_result_list]

    xp, yp = prepare_poly_interpolated_plot(x_list, y_list, plot_pts_size, f_poly_power)
    draw_point_plot(draw, xp, yp, plot_pts_size)

    draw.point((x_axis_cross, y_axis_cross), (255, 0, 0))
    for pt in crosses_result_list:
        draw.point((pt[0], pt[1]), (0, 255, 0))
    # for pt in zip(x_list, y_list):
    #     draw.point((pt[0], pt[1]), (0, 255, 0))
