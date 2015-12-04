__author__ = 'Siarshai'


from math import cos, pi, tan
from os.path import join
from PIL import ImageDraw, Image
from matplotlib import pyplot as plt



def unpack_and_draw_line(draw, line, width, height, color=None, channels=3):
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
        if channels == 3:
            if color is None:
                draw.line((0, fx(0), width, fx(width)), fill=(0, 128, 0))
            else:
                draw.line((0, fx(0), width, fx(width)), fill=color)
        elif channels == 1:
            if color is None:
                draw.line((0, fx(0), width, fx(width)), fill=128)
            else:
                draw.line((0, fx(0), width, fx(width)), fill=color)
        else:
            raise ValueError("Unknown number of channels {} (only 1 and 3 are possible)".format(channels))
    else:
        if channels == 3:
            if color is None:
                draw.line((rho, 0, rho, height), fill=(0, 128, 0))
            else:
                draw.line((rho, 0, rho, height), fill=color)
        elif channels == 1:
            if color is None:
                draw.line((rho, 0, rho, height), fill=128)
            else:
                draw.line((rho, 0, rho, height), fill=color)
        else:
            raise ValueError("Unknown number of channels {} (only 1 and 3 are possible)".format(channels))


def unpack_and_draw_lines(img_src, refined_line_list, channels=3, width=None, height=None):
    """
    Draws lines packed in (alpha, rho) parameters
    :param draw: drawer
    :return: nothing
    """
    if not width or not height:
        #Image passed instead of Drawer
        width = img_src.size[0]
        height = img_src.size[1]
        img_src = ImageDraw.Draw(img_src)
    for line in refined_line_list:
        unpack_and_draw_line(img_src, line, width, height, color=None, channels=channels)


def map_to_image_and_save(image, data, directory, name, suffix, mode="list-type"):
    draw = ImageDraw.Draw(image)
    width = image.size[0]
    height = image.size[1]
    if mode == "list-type":
        for y in range(height):
            for x in range(width):
                draw.point((x, y), data[x][y])
    elif mode == "data-wise":
        for y in range(height):
            for x in range(width):
                draw.point((x, y), data[x, y])
    elif mode == "user-wise":
        for y in range(height):
            for x in range(width):
                draw.point((x, y), data[y, x])
    else:
        raise ValueError("Incorrect mode: {} (only 'list-type', 'data-wise' and 'user-wise' are possible)".format())
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


def draw_point_plot(draw, xp, yp, pts_number, color=None, channels=3):
    prev_pt_x = xp[0]
    prev_pt_y = yp[0]
    for i in range(1, pts_number):
        if channels == 3:
            if color is None:
                draw.line((prev_pt_x, prev_pt_y, xp[i], yp[i]), fill=(128, 0, 0))
            else:
                draw.line((prev_pt_x, prev_pt_y, xp[i], yp[i]), fill=color)
        elif channels == 1:
            if color is None:
                draw.line((prev_pt_x, prev_pt_y, xp[i], yp[i]), fill=128)
            else:
                draw.line((prev_pt_x, prev_pt_y, xp[i], yp[i]), fill=color)
        else:
            raise ValueError("Unknown number of channels {} (only 1 and 3 are possible)".format(channels))
        prev_pt_x = xp[i]
        prev_pt_y = yp[i]