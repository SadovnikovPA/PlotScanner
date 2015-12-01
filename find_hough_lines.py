from integral_image import piece_of_integral_image_buffer
from non_maximal_suppression import apply_recursive_nms

__author__ = 'Siarshai'

from PIL import Image
from math import sin, cos, pi, sqrt
from utils_general import is_local_maximum_circular, debug
from utils_draw import map_to_image_and_save
from kernels import get_gaussian_kernel
import numpy
from scipy.signal import convolve2d
from statistics import median
import sys


def axis_lookup(points_to_visit, data, mask_visited, threshold, width, height):
    x_low = sys.maxsize
    x_high = -1
    y_low = sys.maxsize
    y_high = -1
    while points_to_visit:
        x, y = points_to_visit.pop()
        if not mask_visited[y, x]:
            if x < x_low:
                x_low = x
            if x > x_high:
                x_high = x
            if y < y_low:
                y_low = y
            if y > y_high:
                y_high = y
            mask_visited[y, x] = True
            data[y, x] = 0
            for yy in range(-1, 2):
                for xx in range(-1, 2):
                    if 0 <= x + xx < width and 0 <= y + yy < height:
                        if data[y+yy, x+xx] > threshold:
                            points_to_visit.append((x+xx, y+yy))
    return x_low, x_high, y_low, y_high



def find_crosses(data_h, data_v, image_data):

    assert(len(data_h) == len(data_v))
    assert(len(data_h[0]) == len(data_v[0]))
    height = len(data_h)
    width = len(data_h[0])
    hough_data = numpy.array([[0 for x in range(width)] for y in range(height)])
    nms_mask_visited = numpy.array([[False for x in range(width)] for y in range(height)])

    if debug:
        find_crosses.counter += 1
        image_dump = Image.new("L", (width, height))

    # Points voting for lines
    print("Hough started")
    skew_factor = 15
    for x in range(width):
        for y in range(height):
            if data_v[y, x] != 0:
                for xx in range(width):
                    # norm = abs(x - xx)//skew_factor + 2
                    for yy in range(-abs(x - xx)//skew_factor - 1, abs(x - xx)//skew_factor + 2):
                        if 0 <= y + yy < height:
                            hough_data[y + yy, xx] += 1 #(norm - abs(yy))/float(norm)
            if data_h[y, x] != 0:
                for yy in range(height):
                    # norm = abs(y - yy)//skew_factor + 2
                    for xx in range(-abs(y - yy)//skew_factor - 1, abs(y - yy)//skew_factor + 2):
                        if 0 <= x + xx < width:
                            hough_data[yy, x + xx] += 1 #(norm - abs(xx))/float(norm)
    print("Hough finished")

    result_max = 0
    x_axis_cross = 0
    y_axis_cross = 0
    for y in range(height):
        for x in range(width):
            if hough_data[y, x] > result_max :
                result_max = hough_data[y, x]
                x_axis_cross = x
                y_axis_cross = y

    if debug:
        print("Detected axes cross: ", x_axis_cross, y_axis_cross)

    if debug:
        map_to_image_and_save(image_dump, image_data, "debug/", str(find_crosses.counter), "_before_cross_filter.png", mode = 7)

    cross_size = 7
    cross_center = cross_size//2
    negative_normalizer = 2*cross_size-1
    positive_normalizer = cross_size*cross_size - (4*cross_size - 8) - negative_normalizer
    cross_kernel = numpy.array([[-1.0/negative_normalizer if xxx == cross_center or yyy == cross_center else
                                 (0 if abs(xxx - cross_center) == 1 or abs(yyy - cross_center) == 1 else 1.0/positive_normalizer)
                                 for xxx in range(cross_size)]
                                for yyy in range(cross_size)])
    data_cross = convolve2d(image_data, cross_kernel, mode='same')

    nms_threshold_high = 30
    nms_threshold_low = 10
    nms_threshold_axis_deletion = 2
    for i in range(-6, 7):
        data_cross[y_axis_cross - 1, x_axis_cross + i] = 255
        data_cross[y_axis_cross + i, x_axis_cross - 1] = 255
        data_cross[y_axis_cross, x_axis_cross + i] = 255
        data_cross[y_axis_cross + i, x_axis_cross] = 255
        data_cross[y_axis_cross + 1, x_axis_cross + i] = 255
        data_cross[y_axis_cross + i, x_axis_cross + 1] = 255
    data_cross = convolve2d(data_cross, get_gaussian_kernel(3, 2, True))

    if debug:
        map_to_image_and_save(image_dump, data_cross, "debug/", str(find_crosses.counter), "_before_nms.png", mode = 7)

    x_low, x_high, y_low, y_high  = axis_lookup([(x_axis_cross, y_axis_cross)],
                                                data_cross, nms_mask_visited, nms_threshold_axis_deletion, width, height)
    box = ((y_low, y_high), (x_low, x_high))

    if debug:
        print("Graph box: ", box)

    data_cross = apply_recursive_nms(box, data_cross, nms_mask_visited, nms_threshold_low, nms_threshold_high)

    if debug:
        map_to_image_and_save(image_dump, data_cross, "debug/", str(find_crosses.counter), "_after_nms.png", mode = 7)

    crosses_result_pt_list = []
    crosses_result_val_list = []
    for y in range(box[0][0], box[0][1]):
        for x in range(box[1][0], box[1][1]):
            if data_cross[y, x] > 0:
                crosses_result_pt_list.append((x - cross_center/2, y - cross_center/2, data_cross[y, x]))
                crosses_result_val_list.append(data_cross[y, x])

    threshold_cross_value = median(crosses_result_val_list)/2
    crosses_result_pt_list = [(item[0], item[1]) for item in crosses_result_pt_list if item[2] > threshold_cross_value]

    return x_axis_cross, y_axis_cross, crosses_result_pt_list


find_crosses.counter = 0



def find_hough_lines_in_piece(image_gradient, x_ul, y_ul, x_dr, y_dr, hough_threshold, hough_radius_angle, hough_radius_rho):
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

    pix_grad = image_gradient.load()
    width = x_dr - x_ul
    height = y_dr - y_ul
    max_rho = int(sqrt(width*width + height*height))

    hough_data = []
    for alpha in range(180):
        hough_data.append([0]*2*max_rho)

    hough_line_list = []

    # Points voting for lines
    for x in range(x_ul, x_ul + width):
        for y in range(y_ul, y_ul + height):
            abs_gradient = pix_grad[x, y]
            if abs_gradient != 0:
                for alpha in range(0, 179):
                    rho = int(-(x-x_ul)*sin(alpha*pi/180.0) + (y-y_ul)*cos(alpha*pi/180.0)) + max_rho
                    hough_data[alpha][rho] += 1

    # Translating data to image
    for alpha in range(180):
        for rho in range(2*max_rho):
            if hough_data[alpha][rho] > hough_threshold and is_local_maximum_circular(hough_data, alpha, rho, 180, 2*max_rho, hough_radius_angle, hough_radius_rho):
                coordinate_shift = -(x_ul*sin(alpha*pi/180.0) - y_ul*cos(alpha*pi/180.0))
                hough_line_list.append((alpha, rho + coordinate_shift - max_rho, hough_data[alpha][rho]))

    if len(hough_line_list) > 4:
        hough_line_list.sort(key=lambda x: x[2], reverse=True)
        hough_line_list = [(x[0], x[1]) for x in hough_line_list][0:4]
    else:
        hough_line_list = [(x[0], x[1]) for x in hough_line_list]

    return hough_line_list


def quick_window_detect(processed_gradient_ii, width, height, window_step = 15, border_check_size = 5, border_check_threshold = 2*255, minimal_list_response_threshold = 100*255):

    maximum_value = -1
    maximum_point = (-1, -1)
    window_size = 150  # initial value for quick search window

    #Applying square windows of different size to image
    while maximum_value < minimal_list_response_threshold and window_size < width:
        window_size += window_step
        for y in range(height - window_size):
            for x in range(width - window_size):
                #First we check if borders are clear enough
                buffer_value = piece_of_integral_image_buffer(processed_gradient_ii, width, height, x, y,
                                                              x + window_size,
                                                              y + border_check_size)
                buffer_value += piece_of_integral_image_buffer(processed_gradient_ii, width, height, x,
                                                               y + window_size - border_check_size, x + window_size,
                                                               y + window_size)

                buffer_value += piece_of_integral_image_buffer(processed_gradient_ii, width, height, x, y,
                                                               x + border_check_size,
                                                               y + window_size)
                buffer_value += piece_of_integral_image_buffer(processed_gradient_ii, width, height,
                                                               x + window_size - border_check_size, y, x + window_size,
                                                               y + window_size)
                #Then check if there is enough borders in window
                if buffer_value < border_check_threshold:
                    buffer_value = piece_of_integral_image_buffer(processed_gradient_ii, width, height, x, y,
                                                                  x + window_size,
                                                                  y + window_size)
                    if buffer_value > maximum_value and buffer_value >= minimal_list_response_threshold:
                        maximum_value = buffer_value
                        maximum_point = (x, y)

    #If nothing is found proceed with whole image
    x_window_size = window_size
    y_window_size = window_size
    if maximum_point[0] == -1 or maximum_point[1] == -1:
        maximum_point = (0, 0)
        x_window_size = width
        y_window_size = height

    return maximum_point[0], maximum_point[1], x_window_size, y_window_size