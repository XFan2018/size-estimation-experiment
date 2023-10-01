import argparse
import math
import re

from psychopy import visual, event


def get_args():
    parser = argparse.ArgumentParser("Size Estimation Experiment")
    parser.add_argument("--dataset-path", "-dp", type=str, required=True, help="path to the Pascal dataset")
    parser.add_argument("--category", "-c", type=str, required=True, help="choose the category for the experiment", choices=["cat", "dog", "person", "test"])
    parser.add_argument("--window-size", '-ws', type=str, help="size of the display window, default is 1600,1200", default="1600,1200")
    parser.add_argument("--result-file", '-f', type=str, help="file name to store the experimental results", default="responses")
    parser.add_argument("--assistance-tool", '-at', type=str, help="The type of assistance tool to use. Choose from grid or circle", default="grid",
                        choices=["grid", "circle"])
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


def valid_input(string):
    pattern = r"^\d+(\.\d)?\d*$"
    match = re.fullmatch(pattern, string)
    if not match:
        return False
    num = float(string)
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



