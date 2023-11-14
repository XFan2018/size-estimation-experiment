import argparse
import math
import re
import numpy as np
from PIL import Image
from psychopy import visual, event
from enum import Enum, auto

from xvolume.constants import *


def get_args():
    parser = argparse.ArgumentParser("Size Estimation Experiment")
    parser.add_argument("--dataset-path", "-dp", type=str, required=True, help="path to the Pascal dataset")
    parser.add_argument("--category", "-c", type=str, required=True, help="choose the category for the experiment",
                        choices=['aeroplane', 'bicycle', 'bird', 'boat',
                                 'bottle', 'bus', 'car', 'cat', 'chair',
                                 'cow', 'diningtable', 'dog', 'horse',
                                 'motorbike', 'person', 'pottedplant',
                                 'sheep', 'sofa', 'train', 'tvmonitor', 'test'])
    parser.add_argument("--window-size", '-ws', type=str, help="size of the display window, default is 1200,900", default="1200,900")
    parser.add_argument("--unit", '-u', type=str, help="input unit", default="boxes", choices=["boxes", "percent"])
    parser.add_argument("--result-file", '-f', type=str, help="file name to store the experimental results", default="responses")
    parser.add_argument("--assistance-tool", '-at', type=str, help="The type of assistance tool to use. Choose from grid, and box with absolute size",
                        default="absbox",
                        choices=["grid", "absbox", "none"])
    args = parser.parse_args()
    if args.assistance_tool == "absbox": assert args.unit == "boxes", "Input unit should be boxes if the assistance tool is absolute boxes"
    if args.assistance_tool == "none": args.unit = "percent"
    return args


class Scale(Enum):
    LARGE = auto()
    SMALL = auto()


class AssistanceTool:
    def __init__(self, tool, window):
        self.tool = tool
        self.window = window

        if tool == "grid":
            self.assistance_tool = self.assistance_tool_grid
        elif tool == "absbox":
            self.assistance_tool = self.assistance_tool_abs_boxes
        elif tool == "none":
            self.assistance_tool = self.assistance_tool_none
        else:
            raise NotImplementedError

    def assistance_tool_grid(self, stimulus, scale):
        # assign number of rows and columns as per the aspect ratio
        if scale == Scale.LARGE:
            num_row, num_col = LARGE_SCALE_NUM_ROW, LARGE_SCALE_NUM_COL
        elif scale == Scale.SMALL:
            num_row, num_col = SMALL_SCALE_NUM_ROW, SMALL_SCALE_NUM_COL
        else:
            raise NotImplementedError
        if stimulus.size[0] > stimulus.size[1]:
            # width > height
            row, col = num_row, num_col
        else:
            # width <= height
            row, col = num_col, num_row

        # Draw a grid over the image
        image_width = stimulus.size[0]  # width of the image in pixels
        image_height = stimulus.size[1]  # height of the image in pixels

        # Calculate the distance between lines for the grid
        dx = image_width / col
        dy = image_height / row

        # Horizontal lines
        for i in range(row + 1):
            y_pos = i * dy - (image_height / 2)  # Adjusting position relative to the center of the image
            line = visual.Line(self.window, start=(-image_width / 2, y_pos), end=(image_width / 2, y_pos), lineColor=GRID_LINE_COLOR)
            line.draw()

        # Vertical lines
        for i in range(col + 1):
            x_pos = i * dx - (image_width / 2)  # Adjusting position relative to the center of the image
            line = visual.Line(self.window, start=(x_pos, -image_height / 2), end=(x_pos, image_height / 2), lineColor=GRID_LINE_COLOR)
            line.draw()

    def assistance_tool_abs_boxes(self, stimulus, scale):
        """
        This function provides boxes with absolute size on the image to assist the estimation
        :param mywin: window
        :param stimulus: image stimulus
        :param window_width: window_width
        :return: None
        """
        if scale == Scale.LARGE:
            image_width_over_box_length = LARGE_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        elif scale == Scale.SMALL:
            image_width_over_box_length = SMALL_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        else:
            raise NotImplementedError

        window_width = self.window.size[0]
        image_width, image_height = stimulus.size
        box_size = window_width // image_width_over_box_length  # each box's size is 1/10 of the window width (image width is always 1/2 of the window width)

        # set initial line position
        if scale == Scale.LARGE:
            y_pos = 0.5 * box_size  # center of the image is 0
            x_pos = 0.5 * box_size
        else:
            y_pos = 0
            x_pos = 0

        # Horizontal lines
        while y_pos <= (image_height / 2):
            line = visual.Line(self.window, start=(-image_width / 2, y_pos), end=(image_width / 2, y_pos), lineColor=GRID_LINE_COLOR)
            line.draw()
            line = visual.Line(self.window, start=(-image_width / 2, -y_pos), end=(image_width / 2, -y_pos), lineColor=GRID_LINE_COLOR)
            line.draw()
            y_pos += box_size

        # Vertical lines
        while x_pos <= (image_width / 2):
            line = visual.Line(self.window, start=(x_pos, -image_height / 2), end=(x_pos, image_height / 2), lineColor=GRID_LINE_COLOR)
            line.draw()
            line = visual.Line(self.window, start=(-x_pos, -image_height / 2), end=(-x_pos, image_height / 2), lineColor=GRID_LINE_COLOR)
            line.draw()
            x_pos += box_size

    def assistance_tool_none(self, stimulus, scale):
        pass

    def __call__(self, stimulus, scale):
        self.assistance_tool(stimulus, scale)


class ComputeTool:
    @staticmethod
    def compute_size(response: str, tool: str, unit: str, image_width: float, image_height: float, scale: Scale, window_width: int) -> str:
        """
        This function compute the size of the object based on assistance tool and unit user selected
        :param response: user's response (number of boxes or percentage)
        :param tool: assistance tool
        :param unit: input unit (boxes or percent)
        :param window_width: width of window
        :param image_width: width of image
        :param image_height: width of image
        :return: object size
        """
        if scale == Scale.LARGE:
            percent_per_box = LARGE_SCALE_PERCENT_PER_BOX
            image_width_over_box_length = LARGE_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        elif scale == Scale.SMALL:
            percent_per_box = SMALL_SCALE_PERCENT_PER_BOX
            image_width_over_box_length = SMALL_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        else:
            raise NotImplementedError

        if tool == "absbox":
            # box_size is always 1/10 of window width, image_width is always 1/2 window width
            box_length = window_width / image_width_over_box_length
            num_boxes = float(response)
            size = num_boxes * box_length ** 2 / (image_width * image_height) * 100
        elif tool == "grid":
            if unit == "boxes":
                num_boxes = float(response)
                size = num_boxes * percent_per_box
            else:
                size = float(response)
        elif tool == "none":
            size = float(response)
        else:
            raise NotImplementedError
        return str(round(size, 2))

    @staticmethod
    def compute_ground_truth_image_size(gt, tool, unit, image_width, image_height, scale, window_width):
        if scale == Scale.LARGE:
            percent_per_box = LARGE_SCALE_PERCENT_PER_BOX
            image_width_over_box_length = LARGE_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        elif scale == Scale.SMALL:
            percent_per_box = SMALL_SCALE_PERCENT_PER_BOX
            image_width_over_box_length = SMALL_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        else:
            raise NotImplementedError

        if tool == "absbox":
            box_length = window_width / image_width_over_box_length
            box_area = box_length ** 2
            gt = (gt / 100) * (image_width * image_height) / box_area
        else:
            gt = gt / percent_per_box if unit == "boxes" else gt
        return f"Correct object size is {gt:.2f} {unit} \n Press ENTER to see the next image"

class VerificationTool:
    @staticmethod
    def valid_input(string, unit, tool, image_width, image_height, scale, window_width):
        pattern = r"^(0|[1-9][0-9]*)(\.[0-9]+)?$"
        match = re.fullmatch(pattern, string)
        if not match:
            return False

        if scale == Scale.LARGE:
            image_width_over_box_length = LARGE_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
            number_of_patches = LARGE_SCALE_NUMBER_OF_PATCHES
        elif scale == Scale.SMALL:
            image_width_over_box_length = SMALL_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
            number_of_patches = SMALL_SCALE_NUMBER_OF_PATCHES
        else:
            raise NotImplementedError

        num = float(string)
        if tool == "absbox":
            box_size = window_width / image_width_over_box_length
            box_area = box_size ** 2
            return 0 <= num <= (image_width * image_height / box_area)
        elif tool == "grid":
            if unit == "boxes":
                return 0 <= num <= number_of_patches
            else:
                return 0 <= num <= 100
        else:
            return 0 <= num <= 100


    @staticmethod
    def invalid_input_value(unit, tool, image_width, image_height, scale, window_width):
        if scale == Scale.LARGE:
            number_patches = LARGE_SCALE_NUMBER_OF_PATCHES
            image_width_over_box_length = LARGE_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        elif scale == Scale.SMALL:
            number_patches = SMALL_SCALE_NUMBER_OF_PATCHES
            image_width_over_box_length = SMALL_SCALE_IMAGE_WIDTH_OVER_BOX_LENGTH
        else:
            raise NotImplementedError

        if tool == "absbox":
            box_size = window_width / image_width_over_box_length
            box_area = box_size ** 2
            limit = image_width * image_height / box_area
        else:
            limit = number_patches if unit == "boxes" else 100
        return f"Please enter a valid number between 0 and {math.floor(limit * 10) / 10:.1f}. \nTry again."

    @staticmethod
    def is_digit_or_dot(s: str):
        """
        This function checks whether the input string is a dot or digit
        :param s: input string
        :return: bool
        """
        return s.isdigit() or s == "period"


class DisplayTool:
    @staticmethod
    def display_instructions(window, instruction):
        # Display a prompt above the image
        prompt = visual.TextStim(win=window, text=instruction, pos=(0, 0), height=window.size[0] // 45, wrapWidth=window.size[0] / 1.5, color=PROMPT_COLOR)

        # Draw the prompt
        while True:
            prompt.draw()
            window.flip()
            keys = event.getKeys()
            if 'return' in keys:
                break

    @staticmethod
    def display_training_statistics(window, avg):
        """
        This function used to display the experimental results statistics of the training dataset
        :param window:
        :param avg: average relative error computed from method: training_experimental_results_statistics
        """
        # Display a prompt above the image
        instruction = f"Your average relative error is {avg * 100:.2f}% \n\n press 'Enter' to continue"
        prompt = visual.TextStim(win=window, text=instruction, pos=(0, 0), height=window.size[0] // 40, wrapWidth=window.size[0] / 1.6, color='white')

        # Draw the prompt
        while True:
            prompt.draw()
            window.flip()
            keys = event.getKeys()
            if 'return' in keys:
                break

    @staticmethod
    def display_final_statistics(window, avg, total_time):
        """
        This function used to display the experimental results statistics of the training dataset
        :param window:
        :param avg: average relative error computed from method: experimental_results_statistics
        :param total_time: total time spend on the experiment
        """
        # Display a prompt above the image
        instruction = f"Your average relative error is {avg * 100:.2f}%, Your total time spend on the experiment is {total_time:.2f}s \n\n press 'Enter' to continue"
        prompt = visual.TextStim(win=window, text=instruction, pos=(0, 0), height=window.size[0] // 40, wrapWidth=window.size[0] / 1.6, color='white')

        # Draw the prompt
        while True:
            prompt.draw()
            window.flip()
            keys = event.getKeys()
            if 'return' in keys:
                break

    @staticmethod
    def display_file_not_found(window, filename):
        exception = f"{filename} file is not found in your directory. Press ENTER to quit the experiment."
        # Display a prompt above the image
        prompt = visual.TextStim(win=window, text=exception, pos=(0, 0), height=window.size[0] // 45, wrapWidth=window.size[0] / 1.5, color=PROMPT_COLOR)

        # Draw the prompt
        while True:
            prompt.draw()
            window.flip()
            keys = event.getKeys()
            if 'return' in keys:
                break

class StatisticsTool:
    @staticmethod
    def training_experimental_results_statistics(estimates, gts):
        """
        This function computes the statistics of the experimental results
        :param estimates: user responses of the size estimation
        :param gts: ground truth sizes
        :return: average relative error
        """
        assert len(estimates) == len(gts), "length of responses list and ground truth sizes list should be the same"
        n = len(gts)
        sum = 0
        for estimate, gt in zip(estimates, gts):
            sum += abs(gt - estimate) / gt
        avg = sum / n
        return avg

    @staticmethod
    def experimental_results_statistics(responses):
        """
        This function is used to compute the experimental results statistics of the real dataset
        :param responses: list of tuple. elements of each tuple are image name, estimated size, gt size, and time spent on the current image
        :return: average relative error, total time spend on estimation
        """
        n = len(responses)
        total_time = 0
        sum_error = 0
        for response in responses:
            estimate = float(response[1])
            gt = float(response[2])
            time = float(response[3])
            sum_error += abs(gt - estimate) / gt
            total_time += time
        avg_error = sum_error / n
        return avg_error, total_time


class ImageTool:
    @staticmethod
    def resize_image(original_width, original_length, window_width, image):
        """
        This function is used to resize the original image such that the longer side of the image equals the `img_size` which is 1/2 of the window width
        :param original_width: width of original image
        :param original_length: length of original image
        :param img_size: target image size indicating the longer side of the image should be half of the window width
        :param image: input image
        :return: resized image (ndarray)
        """
        img_size = window_width // 2
        if original_length >= original_width:
            height = int(img_size)
            width = int(img_size * original_width / original_length)
        else:
            width = int(img_size)
            height = int(img_size * original_length / original_width)

        return image.resize((width, height), Image.Resampling.BILINEAR), width, height

    @staticmethod
    def pad_image(window_width, image):
        """
        This function is used to pad the given image with gray values into a square image of size (6 x image_size) x (6 x image_size)
        :param img_size: image_size equals half of the window width.
        :param image: input image to be padded
        :return: return padded image
        """
        img_size = window_width // 2
        box_size = int(img_size / 5)
        padded_image_size = box_size * 6
        image_width, image_height = image.size
        img_arr = np.array(image)

        width_padding = (padded_image_size - image_width) // 2
        height_padding = (padded_image_size - image_height) // 2

        width_offset = 1 if image_width % 2 == 1 else 0
        height_offset = 1 if image_height % 2 == 1 else 0

        padded_image_arr = np.pad(img_arr,
                                  ((height_padding, height_padding + height_offset), (width_padding, width_padding + width_offset), (0, 0)),
                                  constant_values=128)
        padded_image = Image.fromarray(padded_image_arr, "RGB")
        return padded_image



















