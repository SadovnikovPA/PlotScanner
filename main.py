__author__ = 'Siarshai'

from os import listdir, makedirs, unlink
from os.path import isfile, join, exists, dirname
import sys

from PIL import Image, ImageDraw, ImageFilter

from utils_general import ensure_path_exists, map_to_origin_rectangle, debug
from utils_draw import unpack_and_draw_lines, map_to_image_and_save
from gradient import compute_gradient
from find_hough_lines import find_hough_lines_in_piece, quick_window_detect
from integral_image import *
from pixel_analyzer import mark_external_borders
from projective_transform import find_transform_coeffs
from line_splice import line_splice
from corner_detection import find_corners, label_corners
from mark_plot import mark_plot



def prepare_environment():
    argc = len(sys.argv)
    if argc != 3:
        print("ERROR: Wrong number of arguments. " +
              "Usage: script.py path/to/folder/to/process path/to/output/folder")
        exit(1)

    process_folder = sys.argv[1]
    if not exists(dirname(process_folder)):
        print("ERROR: Directory with processed files does not exist")
        exit(1)
    files_to_process = [ (join(process_folder, f), f) for f in listdir(process_folder) if isfile(join(process_folder, f)) ]
    if debug:
        print("Processing files:")
        for filename in files_to_process:
            print(filename[0])

    path_to_output_documents = sys.argv[2]
    try:
        ensure_path_exists(path_to_output_documents)
        #Cleanup
        for the_file in listdir(path_to_output_documents):
            file_path = join(path_to_output_documents, the_file)
            if isfile(file_path):
                unlink(file_path)
    except Exception as e:
        print("ERROR: can not access output directory", str(e))
        exit(1)

    debug_dir = "debug"
    if debug:
        if not exists(debug_dir):
            makedirs(debug_dir)
        else:
            #Cleanup
            for the_file in listdir(debug_dir):
                file_path = join(debug_dir, the_file)
                if isfile(file_path):
                    unlink(file_path)

    return files_to_process, path_to_output_documents, debug_dir



if __name__ == "__main__":

    #Processing script's arguments

    files_to_process, path_to_output_documents, debug_dir = prepare_environment()
    number_of_files_to_process = len(files_to_process)

    #Values important for image processing

    #General
    result_no = 0
    thumbnail_factor = 4

    #Safe margin after sheet extraction
    side_safe_margin = 10

    #Gradienting
    gradient_threshold = 100 #40

    #A4 output size
    a4_size_x = 210*2
    a4_size_y = 297*2

    #Hough search constants
    hough_threshold = 20 #35
    hough_radius_angle = 20
    hough_radius_rho = 40

    #Additional line and line intersection detection
    parallel_lines_margin = 5
    dot_product_threshold = 0.90

    for path, filename in files_to_process:

        result_no += 1
        print("{}/{} - {}".format(result_no, number_of_files_to_process, filename))

        #Opens image and creates proper processing structures
        try:
            origin = Image.open(path)
        except FileNotFoundError:
            #Should not happen unless user modifies pictures in directory path/to/folder/to/process while program is running
            print("ERROR: file " + path + "not found")
            continue
        except EnvironmentError:
            print("ERROR: can not access " + path)
            continue

        #Resizing and smoothing image
        image = origin.copy()
        thumbnail_size = image.width/thumbnail_factor, image.height/thumbnail_factor
        image.thumbnail(thumbnail_size, Image.NONE)
        image = image.filter(ImageFilter.MedianFilter(7))
        draw = ImageDraw.Draw(image)
        width = image.size[0]
        height = image.size[1]
        pix = image.load()

        if debug:
            image.save(join(debug_dir, filename + "_image+median.png"), "PNG")

        # Creates image for gradient then processing it
        image_gradient, gradient_abs = compute_gradient(pix, width, height, gradient_threshold)
        if debug:
            image_gradient.save(join(debug_dir, filename + "_gradient.png"), "PNG")

        external_borders_map = np.zeros((width, height)) #[[0]*height for x in range(width)]
        external_borders_map = mark_external_borders(external_borders_map, gradient_abs, 0, height, 0, width, 25, 1, False)

        if debug:
            map_to_image_and_save(image_gradient, external_borders_map, debug_dir, filename, "_processed_gradient.png", mode=6)

        # Performs quick window search. Thus we obtain approximate location of document.

        processed_gradient_ii = compute_integral_image_buffer(external_borders_map, height, width, mode=4)
        x_pt, y_pt, x_window_size, y_window_size = quick_window_detect(processed_gradient_ii, width, height)

        if debug:
            if x_window_size != y_window_size:
                print("WARNING: quick window search unsuccessful, performing search on whole image")
            draw.rectangle((x_pt, y_pt, x_pt + x_window_size, y_pt + y_window_size), fill=None)
            image.save(join(debug_dir, filename + "_window_detected.png"), "PNG")

        external_borders_map = mark_external_borders(external_borders_map, gradient_abs, y_pt, y_pt + y_window_size, x_pt, x_pt + x_window_size, 1000, 0, True)

        if debug:
            map_to_image_and_save(image_gradient, external_borders_map, debug_dir, filename, "_reprocessed_gradient.png", mode=6)

        # Performs Hough search in located window and splicing lines if several close found
        hough_line_list = find_hough_lines_in_piece(image_gradient, x_pt, y_pt, x_pt + x_window_size, y_pt + y_window_size, hough_threshold, hough_radius_angle, hough_radius_rho)
        refined_line_list = line_splice(hough_line_list, x_window_size, y_window_size, x_pt, y_pt, parallel_lines_margin, dot_product_threshold, hough_radius_angle)

        #Finds corners and marks them as upper-left, upper-right, down-left, down-right
        try:
            corners = find_corners(refined_line_list)
            ur, ul, dr, dl = label_corners(corners)
        except Exception as e:
            print("ERROR: Exception during corner labeling: " + str(e))
            continue

        # Draws detected lines if 'debug' flag is set
        if debug:
            unpack_and_draw_lines(draw, refined_line_list, width, height)
            for corner in corners:
                draw.point(corner, (0, 0, 255))
                image.save(join(debug_dir, filename + "_result.png"), "PNG")

        ul_orig, ur_orig, dl_orig, dr_orig = map_to_origin_rectangle(ul, ur, dl, dr, thumbnail_factor)
        if debug:
            print("Detected document's corners: ul {}, ur {}, dl {}, dr {}".format(ul_orig, ur_orig, dl_orig, dr_orig))

        #Extracts document and marks plot
        try:
            h = find_transform_coeffs(ul_orig, ur_orig, dr_orig, dl_orig, a4_size_x, a4_size_y, side_safe_margin)
            document = origin.transform((a4_size_x, a4_size_y), Image.PERSPECTIVE, h, Image.BICUBIC) #list(h)
            document.save(join(path_to_output_documents, filename + "_extracted.png"), "PNG")
            mark_plot(document)
            document.save(join(path_to_output_documents, filename + "_plot.png"), "PNG")
        except Exception as e:
            print("WARNING: Exception during document extraction: " + str(e))

