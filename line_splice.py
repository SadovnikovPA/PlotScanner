from math import sqrt, sin, cos, asin, acos, pi
from utils import line_instersection, scalar_multiplication, make_ky_line, make_kx_line, unpack_line


def line_splice(hough_line_list, x_window_size, y_window_size, x_pt, y_pt, parallel_lines_margin, dot_product_threshold, hough_radius_angle):
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
        line_splice = [line1]
        j = i + 1
        #Iterates through the rest of lines trying to find nearly parallel lines
        while j < n:
            line2 = hough_line_list[j]
            a1, b1, rho1 = unpack_line(line1)
            a2, b2, rho2 = unpack_line(line2)
            try:
                x, y = line_instersection(a1, b1, rho1, a2, b2, rho2)
            except ValueError as e:
                if str(e) == "Overlap":
                    x, y = x_pt + x_window_size/2, y_pt + y_window_size/2
                if str(e) == "Parallel":
                    if abs(rho2 - rho1) < parallel_lines_margin:
                        x, y = x_pt + x_window_size/2, y_pt + y_window_size/2 #FIXIT
                    else:
                        x, y = -1, -1
            #Lines intersect in rectangle and almost parallel
            if x_pt <= x <= x_pt + x_window_size and y_pt <= y <= y_pt + y_window_size and abs(scalar_multiplication(a1, b1, a2, b2)) > dot_product_threshold:
                line_splice.append(line2)
                del hough_line_list[j]
                n -= 1
            else:
                j += 1
        if len(line_splice) == 1:
            refined_line_list.append(line1)
        else:
            #If more than one line found we should merge them
            #Locates points where lines intersect borders of rectangle and splices them into two points which are
            #used to build resulting line
            x1_avg = 0
            y1_avg = 0
            x2_avg = 0
            y2_avg = 0
            is_vertical = False
            if any([90 - hough_radius_angle < line[0] < 90 + hough_radius_angle for line in line_splice]):
                lines_f = [make_ky_line(sin(line[0]*pi/180.0), -cos(line[0]*pi/180.0), -line[1]) for line in line_splice]
                for line_f in lines_f:
                    x1_avg += line_f(y_pt)
                    y1_avg += y_pt
                    x2_avg += line_f(y_pt + y_window_size)
                    y2_avg += y_pt + y_window_size
                    is_vertical = True
            else:
                lines_f = [make_kx_line(sin(line[0]*pi/180.0), -cos(line[0]*pi/180.0), -line[1]) for line in line_splice]
                for line_f in lines_f:
                    x1_avg += x_pt
                    y1_avg += line_f(x_pt)
                    x2_avg += x_pt + x_window_size
                    y2_avg += line_f(x_pt + x_window_size)
            x1_avg /= len(lines_f)
            y1_avg /= len(lines_f)
            x2_avg /= len(lines_f)
            y2_avg /= len(lines_f)
            dx = x2_avg - x1_avg
            dy = y2_avg - y1_avg
            norm = sqrt(dx*dx + dy*dy)
            if is_vertical:
                alpha = (acos(dx/norm)*180/pi)%180
                rho = -(x1_avg*y2_avg - x2_avg*y1_avg)/norm
            else:
                alpha = (asin(dy/norm)*180/pi)%180
                rho = (x1_avg*y2_avg - x2_avg*y1_avg)/norm
            refined_line_list.append((alpha, rho))
        i += 1
    return refined_line_list