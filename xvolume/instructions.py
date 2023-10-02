import math


def training_instruction(category):
    return f"Before conducting the experiment on the real dataset, you will see 10 {category} images for training purpose. " \
           f"Please estimate the size of the {category} in the image as a percentage of the whole image or number of boxes based on the unit you selected." \
           f"For instance, if you think the object occupies half the image, enter '50'. indicating the {category} occupies 50% of the whole image. " \
           "If you think the object occupies 2.5 boxes enter '2.5'" \
           "There are two types of " \
           "assistance tool you can use to help you with the estimation. Use option --assistance-tool or -at to choose the tool you " \
           "want to use. If you choose 'grid', you can see grids on the image that split the image into 5% patches." \
           "If you choose 'absbox', you will see boxes of absolute sizes on the image. " \
           f"\nPress 'Enter' to run the training experiment. After each example, the correct size of the {category} in the image will be displayed. " \
           "If you are familiar with the experiment already. press 'esc' to skip the training part. "


def estimation_instruction(category):
    return f"Now you can run the experiment on the real dataset. Please estimate the size of the {category} in the image as a percentage of the whole " \
           "image or number of boxes based on the unit you selected. For instance, if you think the object occupies half the image, enter '50' or '50.0'. If you think " \
           "the object occupies 2.5 boxes enter '2.5' " \
           f"\nPress 'Enter' to run the experiment. The correct size of the {category} will NOT be shown to you for the real dataset. "


def invalid_input_value(unit, tool, image_width, image_height):
    if tool == "absbox":
        box_size = image_width / 5.0
        box_area = box_size ** 2
        limit = image_width * image_height / box_area
    else:
        limit = 20 if unit == "boxes" else 100
    return f"Please enter a valid number between 0 and {math.floor(limit*10)/10:.1f}. \nTry again."


def ground_truth_image_size(gt, tool, unit, image_width, image_height):
    if tool == "absbox":
        box_size = image_width / 5
        box_area = box_size ** 2
        gt = (gt / 100) * (image_width * image_height) / box_area
    else:
        gt = gt / 5 if unit == "boxes" else gt
    return f"The correct size of the image is {gt:.1f} {unit} \n\n Do NOT press Enter \nJumping to the next image automatically"


