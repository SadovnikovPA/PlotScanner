__author__ = 'Siarshai'

import numpy as np

def compute_integral_image_buffer(pix, height, width, mode = 1):
    """
    Computes integral image
    :param pix: origin image
    :param height:
    :param width:
    :param mode: 1 if image is grayscale, anything else if 3-channel
    :return: data buffer with integral image
    """
    integral_image_buffer = np.zeros((width, height))

    if mode == 1:
        integral_image_buffer[0, 0] = pix[0, 0]
        for x in range(1, width):
            integral_image_buffer[x, 0] = integral_image_buffer[x-1, 0] + pix[x, 0]
        for y in range(height):
            for x in range(width):
                gray = pix[x, y]
                if y == 0:
                    integral_image_buffer[x, y] = integral_image_buffer[x, y-1] + gray
                else:
                    integral_image_buffer[x, y] = -integral_image_buffer[x-1, y-1] + \
                                                          integral_image_buffer[x, y-1] + \
                                                          integral_image_buffer[x-1, y] + \
                                                          gray

    elif mode == 3:
        integral_image_buffer[0, 0] = (pix[0, 0][0] + pix[0, 0][1] + pix[0, 0][2])/3
        for x in range(1, width):
            integral_image_buffer[x, 0] = integral_image_buffer[x - 1, 0] + (pix[x, 0][0] + pix[x, 0][1] + pix[x, 0][2])/3
        for y in range(height):
            for x in range(width):
                gray = (pix[x, y][0] + pix[x, y][1] + pix[x, y][2])/3
            if y == 0:
                integral_image_buffer[x, y] = integral_image_buffer[x, y-1] + gray
            else:
                integral_image_buffer[x, y] = -integral_image_buffer[x-1, y-1] + \
                                                      integral_image_buffer[x, y-1] + \
                                                      integral_image_buffer[x-1, y] + \
                                                      gray
    elif mode == 4:
        integral_image_buffer[0, 0] = pix[0][0]
        for x in range(1, width):
            integral_image_buffer[x, 0] = integral_image_buffer[x-1, 0] + pix[x][0]
        for y in range(height):
            for x in range(width):
                gray = pix[x][y]
                if y == 0:
                    integral_image_buffer[x, y] = integral_image_buffer[x, y-1] + gray
                else:
                    integral_image_buffer[x, y] = -integral_image_buffer[x-1, y-1] + \
                                                          integral_image_buffer[x, y-1] + \
                                                          integral_image_buffer[x-1, y] + \
                                                          gray
    # elif mode == 6:
    #     integral_image_buffer[0, 0] = pix[0, 0]
    #     for x in range(1, width):
    #         integral_image_buffer[0, x] = integral_image_buffer[0, x-1] + pix[0, x]
    #     for y in range(height):
    #         for x in range(width):
    #             gray = pix[y, x]
    #             if y == 0:
    #                 integral_image_buffer[y, x] = integral_image_buffer[y-1, x] + gray
    #             else:
    #                 integral_image_buffer[y, x] = -integral_image_buffer[y-1, x-1] + \
    #                                                       integral_image_buffer[y-1, x] + \
    #                                                       integral_image_buffer[y, x-1] + \
    #                                                       gray

    return integral_image_buffer


def piece_of_integral_image_buffer(integral_image_buffer, width, height, x1, y1, x2, y2):
    """
    Returns sum of pixels of origin image in rectangle between points (x1, y1), (x2, y2)
    :param height:
    :param integral_image_buffer:
    :param width:
    :param x1:
    :param y1:
    :param x2:
    :param y2:
    :return:
    """
    if x1 < 0 or y1 < 0:
        raise ValueError("Point 1 is behind the image: ({}, {})".format(x1, y1))
    if x2 >= width or y2 >= height:
        raise ValueError("Point 2 is behind the image: ({}, {}) ((w, h) = ({}, {}))".format(x2, y2, width, height))
    if x1 > x2 or y1 > y2:
        raise ValueError("Point 1 is more down-right than 2: pt1 ({}, {}) pt2 ({}, {})".format(x1, y1, x2, y2))
    return integral_image_buffer[x2, y2] + integral_image_buffer[x1, y1] - \
                    integral_image_buffer[x1, y2] - integral_image_buffer[x2, y1]