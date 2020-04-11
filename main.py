from PIL import Image
import numpy as np
from gooey import GooeyParser, Gooey


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


def avg_dice_map(dice_map, cube_res):
    w_map, h_map = dice_map.shape
    cubes_w = w_map // cube_res
    cubes_h = h_map // cube_res
    empty_mat = np.zeros((cubes_w, cubes_h))

    for row in range(0, cubes_w):
        for col in range(0, cubes_h):
            empty_mat[row][col] = (np.sum(dice_map[row * cube_res:(row + 1) * cube_res,
                                                  col * cube_res:(col + 1) * cube_res]))//(cube_res**2)
    return empty_mat


def build_cube(dice_map):
    cfg = load_configuration()
    dice_image_size = int(cfg['Resolution']['dice_image_size'])
    w, h = dice_map.shape
    w1 = w*dice_image_size
    h1 = h*dice_image_size
    final_pic = Image.new('L', (w1, h1))
    cube1 = Image.open(cfg['Assets']['cube_1'])
    cube2 = Image.open(cfg['Assets']['cube_2'])
    cube3 = Image.open(cfg['Assets']['cube_3'])
    cube4 = Image.open(cfg['Assets']['cube_4'])
    cube5 = Image.open(cfg['Assets']['cube_5'])
    cube6 = Image.open(cfg['Assets']['cube_6'])
    for row in range(0, w):
        for col in range(0, h):
            value = dice_map[row][col]
            if value == 1:
                final_pic.paste(cube1, (row*dice_image_size, col*dice_image_size))
            if value == 2:
                final_pic.paste(cube2, (row*dice_image_size, col*dice_image_size))
            if value == 3:
                final_pic.paste(cube3, (row*dice_image_size, col*dice_image_size))
            if value == 4:
                final_pic.paste(cube4, (row*dice_image_size, col*dice_image_size))
            if value == 5:
                final_pic.paste(cube5, (row*dice_image_size, col*dice_image_size))
            if value == 6:
                final_pic.paste(cube6, (row*dice_image_size, col*dice_image_size))
    return final_pic


# Gooey decorator for quick GUI over the main function.
@Gooey(program_name="Dicer: Make beautiful dice portraits",
       body_bg_color="#fceed1",
       header_bg_color="#e1b382")
def main():
    parser = GooeyParser(description="Select an image to process")
    parser.add_argument('Filename', widget="FileChooser")

    args = parser.parse_args()

    path = args.Filename
    image_file = Image.open(path)
    image_file = image_file.convert('L')

    cfg = load_configuration()
    cube_res = int(cfg["Resolution"]["dice_size_px"])

    scaled = scale_image(image_file, cube_res)
    scaled_matrix = np.asarray(scaled)

    new_im, dice_map = div_image(scaled_matrix)
    mat = avg_dice_map(dice_map, cube_res)
    cube_map = build_cube(mat).transpose(Image.TRANSPOSE)
    cube_map.show()


if __name__ == "__main__":
    main()

# TODO:
#   1. Make output file to contain the dice-list separated by lines, for assembly
