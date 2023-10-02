import argparse
import math
import re

from psychopy import visual, event


def get_args():
    parser = argparse.ArgumentParser("Size Estimation Experiment")
    parser.add_argument("--dataset-path", "-dp", type=str, required=True, help="path to the Pascal dataset")
    parser.add_argument("--category", "-c", type=str, required=True, help="choose the category for the experiment", choices=["cat", "dog", "person", "test"])
    parser.add_argument("--window-size", '-ws', type=str, help="size of the display window, default is 1600,1200", default="1600,1200")
    parser.add_argument("--unit", '-u', type=str, help="input unit", default="boxes", choices=["boxes", "percent"])
    parser.add_argument("--result-file", '-f', type=str, help="file name to store the experimental results", default="responses")
    parser.add_argument("--assistance-tool", '-at', type=str, help="The type of assistance tool to use. Choose from grid, and box with absolute size",
                        default="grid",
                        choices=["grid", "absbox"])
    args = parser.parse_args()
    return args


def assistance_tool_grid(mywin, stimulus):
    # assign number of rows and columns as per the aspect ratio
    if stimulus.size[0] > stimulus.size[1]:
        # width > height
        row, col = 4, 5
    else:
        # width <= height
        row, col = 5, 4

    # Draw a grid over the image
    image_width = stimulus.size[0]  # width of the image in pixels
    image_height = stimulus.size[1]  # height of the image in pixels

    # Calculate the distance between lines for the grid
    dx = image_width / col
    dy = image_height / row

    # Horizontal lines
    for i in range(row + 1):
        y_pos = i * dy - (image_height / 2)  # Adjusting position relative to the center of the image
        line = visual.Line(mywin, start=(-image_width / 2, y_pos), end=(image_width / 2, y_pos), lineColor='red')
        line.draw()

    # Vertical lines
    for i in range(col + 1):
        x_pos = i * dx - (image_width / 2)  # Adjusting position relative to the center of the image
        line = visual.Line(mywin, start=(x_pos, -image_height / 2), end=(x_pos, image_height / 2), lineColor='red')
        line.draw()


def assistance_tool(mywin, stimulus, tool):
    if tool == "grid":
        assistance_tool_grid(mywin, stimulus)
    elif tool == "absbox":
        assistance_tool_abs_boxes(mywin, stimulus)
    else:
        raise NotImplementedError


def assistance_tool_abs_boxes(mywin, stimulus):
    """
    This function provides boxes with absolute size on the image to assist the estimation
    :param mywin: window
    :param stimulus: image stimulus
    :return: None
    """
    window_width, window_height = mywin.size
    box_size = window_width // 10  # each box's size is 1/10 of the window width (image width is always 1/2 of the window width)
    image_width, image_height = stimulus.size

    # Horizontal lines
    y_pos = 0.5 * box_size  # center of the image is 0
    while y_pos <= (image_height / 2):
        line = visual.Line(mywin, start=(-image_width / 2, y_pos), end=(image_width / 2, y_pos), lineColor='red')
        line.draw()
        line = visual.Line(mywin, start=(-image_width / 2, -y_pos), end=(image_width / 2, -y_pos), lineColor='red')
        line.draw()
        y_pos += box_size

    # Vertical lines
    x_pos = 0.5 * box_size
    while x_pos < (image_width / 2):
        line = visual.Line(mywin, start=(x_pos, -image_height / 2), end=(x_pos, image_height / 2), lineColor='red')
        line.draw()
        line = visual.Line(mywin, start=(-x_pos, -image_height / 2), end=(-x_pos, image_height / 2), lineColor='red')
        line.draw()
        x_pos += box_size


def assistance_tool_circle(mywin, stimulus):
    # Draw circles over the image which are 1%, 5%, and 10% of the image size
    image_width = stimulus.size[0]  # width of the image in pixels
    image_height = stimulus.size[1]  # height of the image in pixels
    image_size = image_width * image_height

    def compute_redius(size, percentage):
        return math.sqrt(size * percentage / math.pi)

    redius_1 = compute_redius(image_size, 0.01)
    redius_5 = compute_redius(image_size, 0.05)
    redius_10 = compute_redius(image_size, 0.10)
    redius_20 = compute_redius(image_size, 0.20)
    redius_50 = compute_redius(image_size, 0.50)

    circle1 = visual.Circle(mywin, radius=redius_1, fillColor=None, lineColor='red', pos=(0, 0))
    circle5 = visual.Circle(mywin, radius=redius_5, fillColor=None, lineColor='red', pos=(0, 0))
    circle10 = visual.Circle(mywin, radius=redius_10, fillColor=None, lineColor='red', pos=(0, 0))
    circle20 = visual.Circle(mywin, radius=redius_20, fillColor=None, lineColor='red', pos=(0, 0))
    circle50 = visual.Circle(mywin, radius=redius_50, fillColor=None, lineColor='red', pos=(0, 0))

    circle1.draw()
    circle5.draw()
    circle10.draw()
    circle20.draw()
    circle50.draw()


def valid_input(string, unit, tool, image_width, image_height):
    pattern = r"^\d+(\.\d)?\d*$"
    match = re.fullmatch(pattern, string)
    if not match:
        return False
    num = float(string)
    if tool == "absbox":
        box_size = image_width / 5.0
        box_area = box_size ** 2
        return 0 <= num <= (image_width * image_height / box_area)
    else:
        if unit == "boxes":
            return 0 <= num <= 20
        else:
            return 0 <= num <= 100


def display_instructions(window, instruction):
    # Display a prompt above the image
    prompt = visual.TextStim(win=window, text=instruction, pos=(0, 0), height=window.size[0] // 40, wrapWidth=window.size[0] / 1.6, color='white')

    # Draw the prompt
    while True:
        prompt.draw()
        window.flip()
        keys = event.getKeys()
        if 'return' in keys:
            break


def compute_size(response: str, tool: str, unit: str, image_width: float, image_height: float) -> str:
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
    if tool == "absbox":
        # box_size is always 1/10 of window width, image_width is always 1/2 window width
        box_size = image_width / 5.0
        num_boxes = float(response)
        size = num_boxes * box_size ** 2 / (image_width * image_height) * 100
    else:
        if unit == "boxes":
            num_boxes = float(response)
            size = num_boxes * 5
        else:
            size = float(response)
    return str(round(size, 1))


