import math

def training_instruction(category):
    if category == "test":
        category = "cat"
    return f"Before conducting the experiment on the real dataset, you will see 20 {category} images for training purpose. " \
           "\n\nThere are two types of " \
           "assistance tool you can use to help you with the estimation. Use option --assistance-tool or -at to choose the tool you " \
           "want to use. If you choose 'grid', you can see grids on the image that split the image into 5% patches. " \
           "If you choose 'absbox', you will see boxes of absolute sizes. " \
           "If you choose 'grid', you can either use 'percent' or 'boxes' as the unit. Only 'boxes' unit is allowed for tool 'absbox' " \
           f"Please estimate the size of the {category} in the image (exclude the occlusion) as a percentage of the whole image or number of boxes based on the your selected unit. " \
           f"For instance, if you think the object occupies half of the image, enter '50'. indicating the {category} occupies 50% of the whole image. " \
           "If you think the object occupies 2.5 boxes enter '2.5'. " \
           f"\n\nPress 'Enter' to run the training experiment. After each example, the correct size of the {category} in the image will be displayed. " \
           "If you are familiar with the experiment already. press 'Enter', then 'esc' to skip the training part. "


def estimation_instruction(category):
    if category == "test":
        category = "cat"
    return f"Now you can run the experiment on the real dataset. Please estimate the size of the {category} in the image as a percentage of the whole " \
           "image or number of boxes based on your selected unit. " \
           f"\n\nPress 'Enter' to run the experiment. The correct size of the {category} will NOT be shown. " \
           f"You can quit the experiment in the middle using 'esc' key. Your results will not be lost and are saved in the states folder in a JSON file. Make sure you " \
           f"select 'y' to resume your unfinished experiment when you run experiment next time, otherwise your previous intermediate results will be DELETED!! " \
           f"Select 'n' if you want to start a new experiment. You final experimental result (a csv file) will not be generated in the result folder until you finish all the images" \


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
    return f"The correct size of the image is {gt:.2f} {unit} \n\n Press 'Enter' to see the next image"


