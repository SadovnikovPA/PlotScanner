from math import cos, pi, tan
from os.path import join
from PIL import ImageDraw, Image
from matplotlib import pyplot as plt

__author__ = 'Siarshai'


def unpack_and_draw_line(draw, line, width, height):
    """
    Draws lines packed in (alpha, rho) parameters
    :param line: line parameters (alpha, rho)
    :param draw: drawer
    :return: nothing
    """
    alpha = line[0]
    rho = line[1]
    if abs(alpha - 90) > 1:
        b = rho / cos(alpha * pi / 180.0)
        k = tan(alpha * pi / 180.0)
        fx = lambda arg: k * arg + b
        draw.line((0, fx(0), width, fx(width)), fill=(0, 255, 0))
    else:
        draw.line((rho, 0, rho, height), fill=(0, 255, 0))


def unpack_and_draw_lines(draw, refined_line_list, width, height):
    """
    Draws lines packed in (alpha, rho) parameters
    :param draw: drawer
    :return: nothing
    """
    for line in refined_line_list:
        unpack_and_draw_line(draw, line, width, height)


def map_to_image_and_save(image, data, directory, name, suffix, mode=4):
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    if mode == 4:
        for y in range(height):
            for x in range(width):
                draw.point((x, y), data[x][y])
    elif mode == 6:
        for y in range(height):
            for x in range(width):
                draw.point((x, y), data[x, y])
    elif mode == 7:
        for y in range(height):
            for x in range(width):
                draw.point((x, y), data[y, x])
    else:
        raise ValueError("Incorrect mode")
    image.save(join(directory, name + suffix), "PNG")


def convert_data_buffer_to_image(data, name=""):
    image = Image.new("L", (len(data[0]), len(data)))
    draw = ImageDraw.Draw(image)
    for y in range(len(data)):
        for x in range(len(data[0])):
            draw.point((x, y), data[x][y])
    if name != "":
        image.save(name + ".png", "PNG")


def debug_dump_data(data):
    fig, ax = plt.subplots(1, 1)
    ax.imshow(data, cmap='gray')
    ax.set_title('Dump')
    ax.set_axis_off()
    plt.show(block=True)


def draw_point_plot(draw, xp, yp, pts_number, color=(128, 0, 0)):
    prev_pt_x = xp[0]
    prev_pt_y = yp[0]
    for i in range(1, pts_number):
        draw.line((prev_pt_x, prev_pt_y, xp[i], yp[i]), fill=color)
        prev_pt_x = xp[i]
        prev_pt_y = yp[i]