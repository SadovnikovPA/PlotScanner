from math import sin, cos, pi, sqrt
from utils_general import is_local_maximum_circular
from line_splice import splice_lines
import numpy


__author__ = 'Siarshai'


def find_hough_lines_in_piece(image_gradient, x_ul, y_ul, x_dr, y_dr, hough_threshold, hough_radius_angle, hough_radius_rho, number_of_lines=4, mode=1, filter_angle_function=None):
    """
    Applies Hough algorithm to image's gradient in rectangle between points (x_ul, y_ul), (x_dr, y_dr)
    then thresholds Hough data buffer for every pixel in rectangle (-hough_radius_anglel, hough_radius_angle),
     (-hough_radius_rho, hough_radius_rho)
    :param image_gradient:
    :param x_ul:
    :param y_ul:
    :param x_dr:
    :param y_dr:
    :param hough_threshold:
    :param hough_radius_angle:
    :param hough_radius_rho:
    :return: list of lines in (alpha (degrees), rho) format
    """

    # Preparing data
    if mode == 1:
        pix_grad = image_gradient.load()
    else:
        pix_grad = numpy.transpose(image_gradient)

    width = x_dr - x_ul
    height = y_dr - y_ul
    max_rho = int(sqrt(width*width + height*height))

    hough_data = numpy.zeros((180, 2*max_rho), dtype=int)
    hough_line_list = []

    # Points voting for lines
    for x in range(x_ul, x_ul + width):
        for y in range(y_ul, y_ul + height):
            abs_gradient = pix_grad[x, y]
            if abs_gradient != 0:
                for alpha in range(0, 180):
                    rho = int(-(x-x_ul)*sin(alpha*pi/180.0) + (y-y_ul)*cos(alpha*pi/180.0)) + max_rho
                    hough_data[alpha, rho] += 1

    # Translating data to image
    for alpha in range(180):
        for rho in range(2*max_rho):
            if hough_data[alpha, rho] > hough_threshold and is_local_maximum_circular(hough_data, alpha, rho, 180, 2*max_rho, hough_radius_angle, hough_radius_rho):
                coordinate_shift = -(x_ul*sin(alpha*pi/180.0) - y_ul*cos(alpha*pi/180.0))
                hough_line_list.append((alpha, rho + coordinate_shift - max_rho, hough_data[alpha, rho]))

    parallel_lines_margin = 5
    dot_product_threshold = 0.90
    hough_line_list = splice_lines(hough_line_list, width, height, x_ul, y_ul, parallel_lines_margin, dot_product_threshold, hough_radius_angle)

    if filter_angle_function:
        hough_line_list = [line for line in hough_line_list if filter_angle_function(line[0])]

    if number_of_lines <= 0 or len(hough_line_list) < number_of_lines:
        hough_line_list = [(x[0], x[1]) for x in hough_line_list]
    else:
        hough_line_list.sort(key=lambda x: x[2], reverse=True)
        hough_line_list = [(x[0], x[1]) for x in hough_line_list][0:number_of_lines]

    return hough_line_list


