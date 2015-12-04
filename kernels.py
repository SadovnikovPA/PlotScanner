__author__ = 'Siarshai'


from math import sqrt, pi, exp
from scipy.signal import convolve2d
from utils_general import convert_image_to_data_buffer
import numpy


def get_gaussian_kernel(radius, sigma, normalized=True):
    size = 2*radius + 1
    divisor = 2*sigma*sigma
    normalizer = 1/sqrt(2*pi)/sigma
    result_kernel = numpy.array([[normalizer*exp(-((x - radius)**2 + (y - radius)**2)/divisor) for x in range(size)] for y in range(size)])
    if normalized:
        result_kernel = np_normalize_kernel(result_kernel)
    return result_kernel


def get_gaussian_derivative(radius, sigma, derivative_kernel, normalized=True):
    gaussian_kernel = get_gaussian_kernel(radius, sigma, False)
    gaussian_derivative = convolve2d(derivative_kernel, gaussian_kernel)
    if normalized:
        gaussian_derivative = np_normalize_kernel(gaussian_derivative)
    return gaussian_derivative


def get_gaussian_laplasian(radius, sigma, derivative_kernel, normalized=True):
    gaussian_derivative = get_gaussian_derivative(radius, sigma, derivative_kernel, False)
    gaussian_laplasian = convolve2d(derivative_kernel, gaussian_derivative)
    if normalized:
        gaussian_laplasian = np_normalize_kernel(gaussian_laplasian)
    return gaussian_laplasian


def np_normalize_kernel(kernel):
    normalizer_positive = 0
    normalizer_negative = 0
    for x in numpy.nditer(kernel):
         if x > 0:
             normalizer_positive += x
         else:
             normalizer_negative += x
    if normalizer_positive == 0 and normalizer_negative == 0:
        return kernel #nothing to normalize: only zeroes
    normalizer = 1/(normalizer_positive - normalizer_negative)
    for x in numpy.nditer(kernel, op_flags=['readwrite']):
         x[...] = x/normalizer
    return kernel


def apply_kernel_to_image(pix, kernel, width, height, channels=3):
    if channels == 1:
        data_buffer = [[pix[x, y] for x in range(width)] for y in range(height)]
    elif channels == 3:
        data_buffer = [[(pix[x, y][0] + pix[x, y][1] + pix[x, y][2])/3 for x in range(width)] for y in range(height)]
    else:
        data_buffer = pix #passed data buffer
    data_buffer = convolve2d(kernel, data_buffer, mode='same')
    return data_buffer


def apply_apply_gaussian_laplasian_to_image(pix, derivative_kernel, longitude_kernel, width, height, radius = 2, sigma = 1, channels=3, mode="image"):

    gaussian_laplasian = get_gaussian_laplasian(radius, sigma, derivative_kernel, normalized=True)
    gaussian_laplasian = convolve2d(longitude_kernel, gaussian_laplasian)

    if mode == "image":
        image_data = convert_image_to_data_buffer(pix, width, height, channels, orientation="user-wise")
        result_data = convolve2d(image_data, gaussian_laplasian, mode='same')
    elif mode == "buffer":
        result_data = convolve2d(pix, gaussian_laplasian, mode='same')
    else:
        raise ValueError("ERROR: wrong type of image: {} (only 'image' and 'buffer' are possible))".format(mode))

    return result_data




