from math import sqrt, sin, cos, asin, acos, pi
from utils_general import line_instersection, dot_product, make_ky_line, make_kx_line, unpack_line


def mean_angle(angle1, angle2):
    """
    Finds average line guiding angle. Result belongs to [0, pi]
    :param angle1: angle in radians
    :param angle2: angle in radians
    :return: mean angle
    """
    if angle1 < 0:
        n = -angle1//pi + 1
        angle1 += n*pi
    if angle1 > pi:
        n = angle1//pi
        angle1 -= n*pi
    if angle2 < 0:
        n = -angle2//pi + 1
        angle2 += n*pi
    if angle2 > pi:
        n = angle2//pi
        angle2 -= n*pi
    if abs(angle1 - angle2) > pi/2:
        angle1 -= pi
    mean = (angle1 + angle2)/2
    if mean < 0:
        mean += pi
    return mean


def splice_line(a1, b1, rho1, a2, b2, rho2, mode="grad"):
    """
    Splices two lines into bisector one. Lines should be presented in a*x + b*y = rho format
    :param a1: a parameter of first line
    :param b1: a parameter of first line
    :param rho1: a parameter of first line
    :param a2: a parameter of second line
    :param b2: a parameter of second line
    :param rho2: a parameter of second line
    :param mode:
    :return: if mode is "rad" returns (a, b, rho) parameters of line if mode if "grad" returns (angle, rho)
    """
    x, y = line_instersection(a1, b1, rho1, a2, b2, rho2)
    angle1 = acos(b1)
    angle2 = acos(b2)
    angle_new = mean_angle(angle1, angle2)
    a_new = sin(angle_new)
    b_new = cos(angle_new)
    rho_new = (x*a_new + y*b_new)
    if mode == "rad":
        return a_new, b_new, rho_new
    elif mode == "grad":
        return int(acos(-b_new)*180.0/pi), -rho_new
    else:
        raise ValueError("")


def splice_lines(hough_line_list, x_window_size, y_window_size, x_pt, y_pt, parallel_lines_margin, dot_product_threshold, hough_radius_angle):
    """
    Splices close lines in region into one line
    :param hough_line_list:
    :param window_size:
    :param x_pt:
    :param y_pt:
    :param parallel_lines_margin:
    :param dot_product_threshold:
    :param hough_radius_angle:
    :return: list of four lines
    """
    refined_line_list = []
    i = 0
    n = len(hough_line_list)
    #Iterates through lines
    while i < n:
        line1 = hough_line_list[i]
        a1, b1, rho1 = unpack_line(line1)
        j = i + 1
        #Iterates through the rest of lines trying to find nearly parallel lines
        while j < n:
            line2 = hough_line_list[j]
            a2, b2, rho2 = unpack_line(line2)
            try:
                x, y = line_instersection(a1, b1, rho1, a2, b2, rho2)
            except ValueError as e:
                if str(e) == "Overlap":
                    del hough_line_list[j]
                    n -= 1
                    continue
                if str(e) == "Parallel":
                    if abs(rho2 - rho1) < parallel_lines_margin:
                        del hough_line_list[j]
                        n -= 1
                        continue
                    else:
                        j += 1
                        continue
            #Lines intersect in rectangle and almost parallel
            if x_pt <= x <= x_pt + x_window_size and y_pt <= y <= y_pt + y_window_size and abs(dot_product(a1, b1, a2, b2)) > dot_product_threshold:
                mean_weight = (line1[2] + line2[2])/2
                spliced_line = splice_line(a1, b1, rho1, a2, b2, rho2, mode="grad")
                line1 = (spliced_line[0], spliced_line[1], mean_weight)
                del hough_line_list[j]
                n -= 1
            else:
                j += 1
        refined_line_list.append(line1)
        i += 1
    return refined_line_list