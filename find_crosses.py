from statistics import median
import sys
from PIL import Image
import numpy
from scipy.signal import convolve2d
from find_hough_lines import find_hough_lines_in_piece
from kernels import get_gaussian_kernel
from non_maximal_suppression import apply_recursive_nms
from utils_draw import map_to_image_and_save, unpack_and_draw_lines, debug_dump_data
from utils_general import debug, unpack_line, line_instersection
from os.path import join


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

    if len(data_h) != len(data_v) or len(data_h[0]) != len(data_v[0]):
        raise ValueError("find_crosses(): Vertical and horizontal data have different sizes")

    height = len(data_h)
    width = len(data_h[0])
    hough_data = numpy.zeros((height, width), dtype=int)
    nms_mask_visited = numpy.zeros((height, width), dtype=bool)

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
    x_axis_cross = -1
    y_axis_cross = -1
    for y in range(height):
        for x in range(width):
            if hough_data[y, x] > result_max :
                result_max = hough_data[y, x]
                x_axis_cross = x
                y_axis_cross = y

    if x_axis_cross == -1 or y_axis_cross == -1:
        raise ValueError("Axis not found")

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
        if 0 <= y_axis_cross + i < height:
            if 0 <= x_axis_cross - 1:
                data_cross[y_axis_cross + i, x_axis_cross - 1] = 255
            data_cross[y_axis_cross + i, x_axis_cross] = 255
            if x_axis_cross + 1 < width:
                data_cross[y_axis_cross + i, x_axis_cross + 1] = 255
        if 0 <= x_axis_cross + i < width:
            if 0 <= y_axis_cross - 1:
                data_cross[y_axis_cross - 1, x_axis_cross + i] = 255
            data_cross[y_axis_cross, x_axis_cross + i] = 255
            if y_axis_cross + 1 < height:
                data_cross[y_axis_cross + 1, x_axis_cross + i] = 255
    data_cross = convolve2d(data_cross, get_gaussian_kernel(3, 2, True))

    if debug:
        map_to_image_and_save(image_dump, data_cross, "debug/", str(find_crosses.counter), "_before_nms.png", mode = 7)

    x_low, x_high, y_low, y_high = axis_lookup([(x_axis_cross, y_axis_cross)], data_cross, nms_mask_visited, nms_threshold_axis_deletion, width, height)
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

    if not crosses_result_val_list:
        raise ValueError("Axis is found, but not plot points detected")

    threshold_cross_value = median(crosses_result_val_list)/2
    crosses_result_pt_list = [(item[0], item[1]) for item in crosses_result_pt_list if item[2] > threshold_cross_value]

    return x_axis_cross, y_axis_cross, crosses_result_pt_list


find_crosses.counter = 0
