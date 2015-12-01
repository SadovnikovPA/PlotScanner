__author__ = 'Siarshai'

from utils_general import unpack_line, line_instersection, dot_product
from math import hypot


def find_corners(refined_line_list):
    """
    Finds corners (without deciding which is which)
    :param refined_line_list:
    :return: list of corners
    """

    if len(refined_line_list) != 4:
        raise ValueError("ERROR: wrong number of lines")

    base_line = refined_line_list[0]
    i = 1
    j = -1
    max_dot_product = -1
    n = len(refined_line_list)
    while i < n:
        a1, b1, rho1 = unpack_line(base_line)
        a2, b2, rho2 = unpack_line(refined_line_list[i])
        cur_dot_product = abs(dot_product(a1, b1, a2, b2))
        if cur_dot_product > max_dot_product:
            max_dot_product = cur_dot_product
            j = i
        i += 1

    corners = []
    for l in [0, j]:
        k = 0
        while k < n:
            if k != 0 and k != j:
                a1, b1, rho1 = unpack_line(refined_line_list[l])
                a2, b2, rho2 = unpack_line(refined_line_list[k])
                try:
                    corners.append(line_instersection(a1, b1, rho1, a2, b2, rho2))
                except ValueError:
                    #should not happen
                    print("ERROR: parallel lines passed through postprocessor")
                    corners.append((0, 0))
            k += 1

    return corners


def label_corners(corners):
    """
    Finds corners and marks them as upper-left, upper-right, down-left, down-right
    :param corners: list of unlabeled corners
    :return:
    """

    if len(corners) != 4:
        raise ValueError("ERROR: wrong number of corners")

    corners.sort(key=lambda corner: corner[1])

    hypot_1 = hypot(corners[0][0] - corners[1][0], corners[0][1] - corners[1][1])
    hypot_2 = hypot(corners[0][0] - corners[2][0], corners[0][1] - corners[2][1])
    hypot_3 = hypot(corners[0][0] - corners[3][0], corners[0][1] - corners[3][1])

    base_corner = [corners[0], 0]
    if hypot_3 >= hypot_1 and hypot_3 >= hypot_2:
        test1_corner = [corners[1], hypot_1]
        test2_corner = [corners[2], hypot_2]
        furthest_corner = [corners[3], hypot_3]
    if hypot_2 >= hypot_1 and hypot_2 >= hypot_3:
        test1_corner = [corners[1], hypot_1]
        test2_corner = [corners[3], hypot_3]
        furthest_corner = [corners[2], hypot_2]
    if hypot_1 >= hypot_2 and hypot_1 >= hypot_3:
        test1_corner = [corners[3], hypot_3]
        test2_corner = [corners[2], hypot_2]
        furthest_corner = [corners[1], hypot_1]

    if test1_corner[1] < test2_corner[1]:
        if test1_corner[0][0] < test2_corner[0][0]:
            ur = base_corner[0]
            ul = test1_corner[0]
            dr = test2_corner[0]
            dl = furthest_corner[0]
        else:
            ur = test1_corner[0]
            ul = base_corner[0]
            dr = furthest_corner[0]
            dl = test2_corner[0]
    else:
        if test1_corner[0][0] < test2_corner[0][0]:
            ur = test2_corner[0]
            ul = base_corner[0]
            dr = furthest_corner[0]
            dl = test1_corner[0]
        else:
            ur = base_corner[0]
            ul = test2_corner[0]
            dr = test1_corner[0]
            dl = furthest_corner[0]

    return ur, ul, dr, dl