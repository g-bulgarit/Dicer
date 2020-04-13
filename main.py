from gooey import GooeyParser, Gooey
from algo import *


# Gooey decorator for quick GUI over the main function.
@Gooey(program_name="Dicer: Make beautiful dice portraits",
       body_bg_color="#fceed1",
       header_bg_color="#e1b382")
def main():
    parser = GooeyParser(description="Select an image to process")
    parser.add_argument('path', metavar='File', widget="FileChooser", help="Browse to your file.")
    parser.add_argument('dice_color', metavar='Dice Color', widget="Dropdown",
                        help="Choose the color of dice to use.",
                        choices=["Black", "White"],
                        default="Black")

    parser.add_argument('--dice_size',
                        metavar="Dice Size",
                        type=int,
                        help="Dice size in millimeters, 16mm is the standard size.\n"
                             "Other sizes include 12mm and 8mm",
                        default=16,
                        gooey_options={
                            'validator': {
                                'test': '0<int(user_input)',
                                'message': 'Dice size can\'t be negative!'
                            }
                        }
                        )
    parser.add_argument('--dice_px_ratio',
                        metavar="Cube to Pixel Ratio",
                        type=int,
                        help="How many pixels to consume with one cube.\n"
                             "Increasing this value changes the result drastically.\n"
                             "Generally - small value = more detail.",
                        default=15,
                        gooey_options={
                            'validator': {
                                'test': '0<int(user_input)',
                                'message': 'The ratio can\'t be negative!'
                            }
                        }
                        )

    # Parse arguments from GUI
    args = parser.parse_args()
    physical_size = args.dice_size
    cube_res = args.dice_px_ratio
    dice_color = args.dice_color
    path = args.path

    # Open the image and convert to B/W
    image_file = Image.open(path)
    image_file = image_file.convert('L')

    # Rescale and numpy-ify
    scaled = scale_image(image_file, cube_res)
    scaled_matrix = np.asarray(scaled)

    # Make it out of dice!
    dice_map = div_image(scaled_matrix)

    # If the dice color is white, invert the dice map
    if dice_color == "White":
        dice_map = 7-dice_map

    final_dice_matrix = avg_dice_map(dice_map, cube_res)
    cube_map = build_cube(final_dice_matrix, physical_size, dice_color)
    cube_map.show()

    # Save output map to file
    compile_build_instructions(final_dice_matrix, args)



if __name__ == "__main__":
    main()

# TODO:
#   1. Make output file to contain the dice-list separated by lines, for assembly [V]
#   2. Work on changing dice orientation for the asymmetric numbers 2,3,6
#   3. Add white dice as an option. [V]
