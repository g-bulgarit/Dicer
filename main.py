from PIL import Image
import numpy as np
import configparser

def load_configuration():
    import configparser
    config_reader = configparser.ConfigParser()
    config_reader.read('config.ini')
    return config_reader

def scale_image(image , cube_size):
    image_w , image_h = image.size
    scale_h = image_h//cube_size #how many cube fits in high
    new_h = scale_h*cube_size
    scale_w = image_w // cube_size  # how many cube fits in w
    new_w = scale_w * cube_size
    new_image = image.resize((new_w , new_h))
    return new_image


cfg = load_configuration()
cube_res = int (cfg["Resolution"]["dice_size_px"])

image_file = Image.open("Assets/goku.jpg")
image_file = image_file.convert('L')
scaled = scale_image(image_file , cube_res)
image_matrix = np.asarray(scaled)