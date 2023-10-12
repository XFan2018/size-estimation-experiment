import math

from xvolume.constants import *
from xvolume.utils import Scale


def training_instruction(category):
    if category == "test":
        category = "cat"
    return f"""
    Before conducting the experiment on the real dataset, you will see 20 {category} images for training purpose. 
    \n\nThere are two types of assistance tool so-called 'absbox' and 'grid' you can use to help you with the estimation. Use option --assistance-tool or -at to choose the tool. 'grid' tool displays grids on the image that split the image into 5% patches. 'absbox' tool shows boxes of absolute sizes. With 'grid', you can either use 'percent' or 'boxes' as the unit (choose with option --unit or -u from 'boxes' and 'percent'). Only 'boxes' unit is allowed for 'absbox' tool. Please estimate the size of the {category} in the image (exclude the occlusion) as a percentage of the whole image or number of boxes based on your selected unit. For instance, if you think the object occupies half of the image, enter '50'. indicating the {category} occupies 50% of the whole image. If you think the object occupies 2.5 boxes enter '2.5'. 
    \n\nDuring the experiment, you can use 'up' and 'down' arrow keys to toggle the size of assistant boxes. Only two scales are available. Your estimation will be adjusted automatically based on the box size. 
    \n\nPress 'Enter' to run the training experiment. After each example, the correct size of the {category} in the image will be displayed. If you are familiar with the experiment already. Press 'Enter', then 'esc' to skip the training part. 
    """


def estimation_instruction(category):
    if category == "test":
        category = "cat"
    return f"""
    Now you can run the experiment on the real dataset. Please estimate the size of the {category} in the image as a percentage of the whole image or number of boxes based on your selected unit. 
    \n\nPress 'Enter' to run the experiment. The correct size of the {category} will NOT be shown. You can quit the experiment in the middle using 'esc' key. Your results will not be lost and are saved in the states folder in a JSON file. Make sure you select 'y' to resume your unfinished experiment when you run experiment next time, otherwise your previous intermediate results will be DELETED!! Select 'n' if you want to start a new experiment. Your final experimental result (a csv file) will not be generated in the result folder until you finish all the images. It's highly recommended that you name your result file with option -f <name> (without extension), such that you know the exact name of the result file if you run the experiment multiple times (default result file name is "responses"). It also prevents previous result file being overwritten by a new experimental result with the same name. 
    """
