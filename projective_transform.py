from numpy.linalg import solve
from numpy import array


def find_transform_coeffs(ul, ur, dr, dl, a4_size_x, a4_size_y, margin):
    """
    Prepares and solves linear system for h-parameters of projective transform given image to A4 sheet (placed vertically)
    :param ul: upper left corner of A4 sheet on image
    :param ur: upper right corner of A4 sheet on image
    :param dr: down right corner of A4 sheet on image
    :param dl: down left corner of A4 sheet on image
    :param a4_size_x: given width of a4 sheet
    :param a4_size_y: given height of a4 sheet
    :return: list of h-coeffs
    """

    x1t = dl[0]
    y1t = dl[1]

    x2t = ul[0]
    y2t = ul[1]

    x3t = ur[0]
    y3t = ur[1]

    x4t = dr[0]
    y4t = dr[1]

    x1 = -margin
    y1 = a4_size_y + margin

    x2 = -margin
    y2 = -margin

    x3 = a4_size_x + margin
    y3 = -margin

    x4 = a4_size_x + margin
    y4 = a4_size_y + margin

    a = array([[x1, y1, 1, 0, 0, 0, -x1t*x1, -x1t*y1],
               [x2, y2, 1, 0, 0, 0, -x2t*x2, -x2t*y2],
               [x3, y3, 1, 0, 0, 0, -x3t*x3, -x3t*y3],
               [x4, y4, 1, 0, 0, 0, -x4t*x4, -x4t*y4],
               [0, 0, 0, x1, y1, 1, -y1t*x1, -y1t*y1],
               [0, 0, 0, x2, y2, 1, -y2t*x2, -y2t*y2],
               [0, 0, 0, x3, y3, 1, -y3t*x3, -y3t*y3],
               [0, 0, 0, x4, y4, 1, -y4t*x4, -y4t*y4]
               ])

    b = array([x1t, x2t, x3t, x4t, y1t, y2t, y3t, y4t])

    h = solve(a, b)

    return h

