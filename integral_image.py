__author__ = 'Siarshai'

import numpy as np

def compute_integral_image_buffer(pix, height, width, mode = "image"):
    """
    Computes integral image
    :param pix: origin image
    :param height:
    :param width:
    :param mode: 1 if image is grayscale, anything else if 3-channel
    :return: data buffer with integral image
    """
    integral_image_buffer = np.zeros((width, height))

    if mode == "image":
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
    elif mode == "buffer":
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
    else:
        raise ValueError("ERROR: wrong type of image: {} (only 'image' and 'buffer' are possible))".format(mode))

    return integral_image_buffer


def integral_image_piece(integral_image_buffer, width, height, x1, y1, x2, y2):
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


def integral_image_window_detect(processed_gradient_ii, width, height, window_step = 15, border_check_size = 5, border_check_threshold = 2*255, minimal_list_response_threshold = 100*255):

    maximum_value = -1
    maximum_point = (-1, -1)
    window_size = 150  # initial value for quick search window

    #Applying square windows of different size to image
    while maximum_value < minimal_list_response_threshold and window_size < width:
        window_size += window_step
        for y in range(height - window_size):
            for x in range(width - window_size):
                #First we check if borders are clear enough
                buffer_value = integral_image_piece(processed_gradient_ii, width, height, x, y,
                                                              x + window_size,
                                                              y + border_check_size)
                buffer_value += integral_image_piece(processed_gradient_ii, width, height, x,
                                                               y + window_size - border_check_size, x + window_size,
                                                               y + window_size)

                buffer_value += integral_image_piece(processed_gradient_ii, width, height, x, y,
                                                               x + border_check_size,
                                                               y + window_size)
                buffer_value += integral_image_piece(processed_gradient_ii, width, height,
                                                               x + window_size - border_check_size, y, x + window_size,
                                                               y + window_size)
                #Then check if there is enough borders in window
                if buffer_value < border_check_threshold:
                    buffer_value = integral_image_piece(processed_gradient_ii, width, height, x, y,
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