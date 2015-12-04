__author__ = 'Siarshai'


def apply_recursive_nms(box, data, mask_visited, threshold_low, threshold_high):
    """
    Detects regions with value above threshold_low. Nullifis them, remaining only local maximum point only if it's above
     threshold_high
    :param box:
    :param data:
    :param mask_visited:
    :param threshold_low:
    :param threshold_high:
    :return:
    """
    for y in range(box[0][0], box[0][1]):
        for x in range(box[1][0], box[1][1]):
            if not mask_visited[y, x]:
                if data[y, x] > threshold_low:
                    val_cluster_max, x_cluster_max, y_cluster_max = nms_inner([(x, y)], box, data, mask_visited, threshold_low, threshold_high)
                    if val_cluster_max > threshold_high:
                        data[y_cluster_max, x_cluster_max] = val_cluster_max
                else:
                    mask_visited[y, x] = True
                    data[y, x] = 0
    return data


def nms_inner(points_to_visit, box, data, mask_visited, threshold_low, threshold_high):
    val_cluster_max = -1
    x_cluster_max = -1
    y_cluster_max = -1
    while points_to_visit:
        x, y = points_to_visit.pop()
        if not mask_visited[y, x]:
            mask_visited[y, x] = True
            val = data[y, x]
            data[y, x] = 0
            if val > val_cluster_max:
                val_cluster_max = val
                x_cluster_max = x
                y_cluster_max = y
            for yy in range(-1, 2):
                for xx in range(-1, 2):
                    if box[1][0] <= x + xx < box[1][1] and box[0][0] <= y + yy < box[0][1]:
                        if data[y+yy, x+xx] > threshold_low:
                            points_to_visit.append((x+xx, y+yy))
    if val_cluster_max < threshold_high:
        val_cluster_max = -1
    return val_cluster_max, x_cluster_max, y_cluster_max