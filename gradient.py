from math import sqrt, atan2
from PIL import Image, ImageDraw
from utils import fill_the_gaps, filter_2_dr


def apply_sobel_base(p00, p01, p02, p20, p21, p22):
    return p20 + 2*p21 + p22 - p00 - 2*p01 - p02

def apply_sobel_horizontal(pix, x, y, i):
    return apply_sobel_base(pix[x-1, y-1][i], pix[x-1, y][i], pix[x-1, y+1][i],
                      pix[x+1, y-1][i], pix[x+1, y][i], pix[x+1, y+1][i])

def apply_sobel_vertical(pix, x, y, i):
    return apply_sobel_base(pix[x-1, y-1][i], pix[x, y-1][i], pix[x+1, y-1][i],
                      pix[x-1, y+1][i], pix[x, y+1][i], pix[x+1, y+1][i])



def compute_gradient(pix, width, height, gradient_threshold):
    """
    Computes thresholded gradient of given image
    :param pix: image
    :param width:
    :param height:
    :param gradient_threshold:
    :return: processed image, gradient absolute value buffer list, gradient anglebuffer list
    """

    image_gradient = Image.new("L", (width, height))
    draw_gradient = ImageDraw.Draw(image_gradient)

    gradient_abs_list = []
    gradient_angle_list = []

    # Applies Sobel filter to image then thresholds. Both absolute value and direction get recorded
    for i in range(width):
        tmp_gradient_abs_list = []
        tmp_gradient_angle_list = []
        for j in range(height):
            if i == 0 or j == 0 or i == width - 1 or j == height - 1:
                tmp_gradient_abs_list.append(0)
                tmp_gradient_angle_list.append((0, 0, 0, 0, 0, 0))
            else:
                derivative_xrh = apply_sobel_horizontal(pix, i, j, 0)
                derivative_yrh = apply_sobel_vertical(pix, i, j, 0)
                derivative_xgh = apply_sobel_horizontal(pix, i, j, 1)
                derivative_ygh = apply_sobel_vertical(pix, i, j, 1)
                derivative_xbh = apply_sobel_horizontal(pix, i, j, 2)
                derivative_ybh = apply_sobel_vertical(pix, i, j, 2)
                weightr = derivative_xrh*derivative_xrh + derivative_yrh*derivative_yrh
                weightg = derivative_xgh*derivative_xgh + derivative_ygh*derivative_ygh
                weightb = derivative_xbh*derivative_xbh + derivative_ybh*derivative_ybh
                abs_gradient = int(sqrt(weightr + weightg + weightb))
                weightsum = weightr + weightg + weightb
                if weightsum != 0:
                    weightr /= weightsum
                    weightg /= weightsum
                    weightb /= weightsum
                angler = atan2(derivative_yrh, derivative_xrh)
                angleg = atan2(derivative_ygh, derivative_xgh)
                angleb = atan2(derivative_ybh, derivative_xbh)
                tmp_gradient_abs_list.append(255 if abs_gradient > gradient_threshold else 0)
                tmp_gradient_angle_list.append((angler, angleg, angleb, weightr, weightg, weightb))
        gradient_abs_list.append(tmp_gradient_abs_list)
        gradient_angle_list.append(tmp_gradient_angle_list)

    # Deletes stray gradient specks
    gradient_abs_list = fill_the_gaps(gradient_abs_list, 0, width, 0, height)
    gradient_abs_list = fill_the_gaps(gradient_abs_list, 0, width, 0, height)
    gradient_abs_list = fill_the_gaps(gradient_abs_list, 0, width, 0, height)
    gradient_abs_list = filter_2_dr(gradient_abs_list, width, height, min)
    gradient_abs_list = fill_the_gaps(gradient_abs_list, 0, width, 0, height)

    for x in range(width):
        for y in range(height):
            draw_gradient.point((x, y), gradient_abs_list[x][y])

    return image_gradient, gradient_abs_list, gradient_angle_list