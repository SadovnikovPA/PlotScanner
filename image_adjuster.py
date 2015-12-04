from os import listdir
from os.path import isfile, join
import sys
from PIL import Image

# Auxiliary for resizing images

process_folder = sys.argv[1]
suffix = sys.argv[2]
files_to_process = [ (join(process_folder, f), f) for f in listdir(process_folder) if isfile(join(process_folder, f)) ]

i = 0
n = len(files_to_process)
for path, filename in files_to_process:
    i += 1
    print("processing: {}, {}/{}".format(filename, i, n))
    image = Image.open(path)
    thumbnail_size = (1200, 1600)
    image.thumbnail(thumbnail_size, Image.BICUBIC)
    image.save(join(process_folder, str(i) + suffix + ".png"), "PNG")