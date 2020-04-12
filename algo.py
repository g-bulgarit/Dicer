from PIL import Image
import numpy as np


def load_configuration():
    """
    Load configuration from the config file.
    :return: configparser object.
    """

    import configparser
    config_reader = configparser.ConfigParser()
    config_reader.read('config.ini')
    return config_reader


def scale_image(image, cube_size):
    """
    Scale the input image to a whole number of cubes with minimal stretch.
    :param image: PIL Image object.
    :param cube_size: Cube size from configuration, int.
    :return: A scaled PIL Image.
    """
    image_w, image_h = image.size

    scale_h = image_h // cube_size  # Amount of cubes that fit in the height
    new_h = scale_h * cube_size

    scale_w = image_w // cube_size   # Amount of cubes that fit in the width
    new_w = scale_w * cube_size

    new_image = image.resize((new_w, new_h))  # Resize the image accordingly.
    return new_image


def div_image(matrix):
    """
    Split the image by threshold.
    :param matrix: A numpy array of a B/W image.
    :return: A new matrix, thresholded to 6 values.
    """
    zero_mat = np.zeros(matrix.shape)  # Construct a zero matrix
    dice_map = np.zeros(matrix.shape)  # Construct a zero matrix

    image_top = np.max(matrix)  # Get min and max pixels
    image_bottom = np.min(matrix)

    delta = (image_top-image_bottom)//6
    for i in range(0, 6):
        zero_mat[matrix >= i*delta] = (255*i//6)  # Let all pixels above the threshold be one color.
        dice_map[matrix >= i*delta] = (i+1)  # Let all pixels above the threshold be one color.

    return zero_mat, dice_map


def avg_dice_map(thresh_img, cube_res):
    """
    Produces a matrix made up of only numbers from 1-6,
    corresponding to the values on the faces of the dice.
    :param thresh_img: The 6-toned image to process.
    :param cube_res: Dice to pixel ratio from GUI.
    :return: A dice matrix
    """

    w_map, h_map = thresh_img.shape
    cubes_w = w_map // cube_res
    cubes_h = h_map // cube_res
    dice_matrix = np.zeros((cubes_w, cubes_h))

    for row in range(0, cubes_w):
        for col in range(0, cubes_h):
            dice_matrix[row][col] = (np.sum(thresh_img[row * cube_res:(row + 1) * cube_res,
                                                       col * cube_res:(col + 1) * cube_res]))\
                                     // (cube_res**2)
    return dice_matrix


def build_cube(dice_map, physical_size):
    """
    Create a cube image from a cube map.
    :param dice_map: A matrix that contains dice information.
    :param physical_size: size of a single dice, in millimeters - used only for
                          actual size calculation.
    :return: the final image, made up from dice.
    """

    cfg = load_configuration()
    dice_image_size = int(cfg['Resolution']['dice_image_size'])
    h, w = dice_map.shape
    w1 = w * dice_image_size
    h1 = h * dice_image_size

    print(f"{w} cubes wide,\n"
          f"{h} cubes tall, \n"
          f"{w*h} total cubes.\n")

    # Physical properties
    print(f"{w * physical_size} [mm] wide,\n"
          f"{h * physical_size} [mm] tall. \n")

    # Create the final image and load all dice pictures to memory.
    final_pic = Image.new('L', (w1, h1))
    cube1 = Image.open(cfg['Assets']['cube_1'])
    cube2 = Image.open(cfg['Assets']['cube_2'])
    cube3 = Image.open(cfg['Assets']['cube_3'])
    cube4 = Image.open(cfg['Assets']['cube_4'])
    cube5 = Image.open(cfg['Assets']['cube_5'])
    cube6 = Image.open(cfg['Assets']['cube_6'])

    # Place dice
    for row in range(0, h):
        for col in range(0, w):
            value = dice_map[row][col]
            if value == 1:
                final_pic.paste(cube1, (col * dice_image_size, row * dice_image_size))
            if value == 2:
                final_pic.paste(cube2, (col * dice_image_size, row * dice_image_size))
            if value == 3:
                final_pic.paste(cube3, (col * dice_image_size, row * dice_image_size))
            if value == 4:
                final_pic.paste(cube4, (col * dice_image_size, row * dice_image_size))
            if value == 5:
                final_pic.paste(cube5, (col * dice_image_size, row * dice_image_size))
            if value == 6:
                final_pic.paste(cube6, (col * dice_image_size, row * dice_image_size))
    return final_pic


def compile_build_instructions(dice_map, gui_args):
    """
    Takes in the dice matrix,
    compiles a text file with the cubes for each row separated by commas, rows separated by lines.
    :param dice_map: The matrix that contains the dice information for the given parameters.
    :param gui_args: Args from the GUI, to be used for the filename.
    :return:
    """
    path = gui_args.path
    phys_size = str(gui_args.dice_size)
    ratio = str(gui_args.dice_px_ratio)
    filename = path.split("\\")[-1].split(".")[0] + "_" + phys_size + "_" + ratio + ".txt"
    with open(filename, "w+") as fp:
        for idx, row in enumerate(dice_map.astype(int)):

            # Separate to 8 groups for easier assembly
            row_lst = str(row)[1:-1].split(" ")
            block_separator = len(row) // 8

            # Insert separators
            for loc in range(len(row), 0, -1 * block_separator):
                row_lst.insert(loc, " [X] ")

            # Write to file
            line = "Line " + str(idx + 1) + ": " + " ".join(row_lst) + "\n"
            fp.write(line)
