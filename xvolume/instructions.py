def training_instruction(category):
    return f"Before conducting the experiment on the real dataset, you will see 10 {category} images for training purpose. " \
           f"Please estimate the size of the {category} in the image as a percentage of the whole image. " \
           f"For instance, if you think the object occupies half the image, enter '50'. indicating the {category} occupies 50% of the whole image. " \
           "Please provide your estimate to the nearest whole number. There are two types of " \
           "assistance tool you can use to help you with the estimation. Use option --assistance-tool or -at to choose the tool you " \
           "want to use. If you choose 'grid', you can see grids on the image that split the image into 5% patches." \
           "If you choose 'circle' you will see 5 circles on the image representing the 1%, 5%, 10%, 20%, and 50% area of the image. " \
           f"Press 'Enter' to run the training experiment. After each example, the correct size of the {category} in the image will be displayed. " \
           "If you are familiar with the experiment already. press 'esc' to skip the training part. "


def estimation_instruction(category):
    return f"Now you can run the experiment on the real dataset. Please estimate the size of the {category} in the image as a percentage of the whole " \
           "image. For instance, if you think the object occupies half the image, enter '50'. " \
           "Please provide your estimate to the nearest whole number. There are two types of " \
           "assistance tool you can use to help you with the estimation. Use option --assistance-tool or -at to choose the tool you " \
           "want to use. If you choose 'grid', you can see grids on the image that split the image into 5% patches. " \
           "If you choose 'circle' you will see 5 circles on the image representing 1%, 5%, 10%, 20%, and 50% area of the image. " \
           f"Press 'Enter' to run the experiment. The correct size of the {category} will NOT be shown to you for the real dataset. "


def invalid_input_value():
    return "Please enter a valid number between 0 and 100. \nTry again."


def ground_truth_image_size(gt):
    return f"The correct size of the image is {gt:.1f} \n\n Do NOT press Enter \nJumping to the next image automatically"
