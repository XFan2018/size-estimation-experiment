import math

from xvolume.constants import *
from xvolume.utils import Scale


def training_instruction(category):
    if category == "test":
        category = "cat"
    return f"""
    TRAINING EXPERIMENT INSTRUCTIONS
    \n Before conducting the experiment on the real dataset, you will see 20 {category} images for training purpose. 
    \n There are two types of assistance tool named 'absbox' and 'grid' to help you with the estimation. Use option --assistance-tool or -at to choose the tool. 'grid' tool displays grids on the image that split the image into 5% patches. 'absbox' tool shows boxes of absolute sizes. With 'grid', you can either use 'percent' or 'boxes' as the unit (choose with option --unit or -u from 'boxes' and 'percent'). Only 'boxes' unit is allowed for 'absbox' tool. Please estimate the size of the {category} in the image (exclude any occlusion) as a percentage of the whole image or number of boxes based on your selected unit. For instance, if you use boxes (default) as the unit, enter '2.5' if the object occupies 2.5 boxes. If percent is the unit, enter '50' if the object occupies half of the image. 
    \n During the experiment, you can use UP and DOWN arrow keys to toggle the size of assistant boxes. Only two scales are available. Your estimation will be adjusted automatically based on the box size. 
    \n Press ENTER to run the training experiment. After each example, the correct size of the {category} in the image will be displayed. If you are familiar with the experiment already. Press ENTER, then ESC key to skip the training part. 
    """


def estimation_instruction(category):
    if category == "test":
        category = "cat"
    return f"""
    EXPERIMENT INSTRUCTIONS
    \n Now you can run the experiment on the real dataset. Please estimate the size of the {category} in the image as a percentage of the whole image or number of boxes based on your selected unit. 
    \n Press ENTER to run the experiment. The correct size of the {category} will NOT be shown. You can quit the experiment in the middle using ESC key. Your intermediate results will not be lost and are saved in the states folder as a JSON file. Make sure you press Y key to resume your unfinished experiment, otherwise your previous intermediate results will be DELETED!! Press N key if you want to start a new experiment. Your final experimental result (a CSV file) will not be generated (in the result folder) until you finish all the images. It's highly recommended that you name your result file with option -f <name> (without extension), such that you know the exact name of the result file if you run the experiment multiple times (default result file name is "responses"). It also prevents previous result file from being overwritten by a new file with the same name. 
    """
