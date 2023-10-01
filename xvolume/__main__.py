import math
from .class_mapping import Index
from PIL import Image
from psychopy import visual, core, event
import os
import csv
import json
import argparse
import numpy as np
from .instructions import *



parser = argparse.ArgumentParser("Size Estimation Experiment")
parser.add_argument("--dataset-path", "-dp", type=str, required=True, help="path to the Pascal dataset")
parser.add_argument("--category", "-c", type=str, required=True, help="choose the category for the experiment", choices=["cat", "dog", "person", "test"])
parser.add_argument("--window-size", '-ws', type=str, help="size of the display window, default is 1600,1200", default="1600,1200")
parser.add_argument("--result-file", '-f', type=str, help="file name to store the experimental results", default="responses")
parser.add_argument("--assistance-tool", '-at', type=str, help="The type of assistance tool to use. Choose from grid or circle", default="grid",
                    choices=["grid", "circle"])
args = parser.parse_args()

DATASET_PATH = args.dataset_path
INDEX = Index.get_index(args.category)
NEW_IMG_WIDTH = int(args.window_size.split(",")[0]) // 2
current_path = os.getcwd()

def main():
    # Setup the Window
    assert "," in args.window_size and len(args.window_size.split(",")) == 2 and all([s.isdigit() for s in args.window_size.split(",")]), \
        "window size argument must be two positive integers separated by ',' representing the display window size."

    mywin = visual.Window(list(map(int, args.window_size.split(","))), monitor="testMonitor", units="pix")

    # Specify your image directory
    base_dir = DATASET_PATH
    image_dir = os.path.join(base_dir, "JPEGImages" + os.sep)
    gt_dir = os.path.join(base_dir, "SegmentationClassAug" + os.sep)
    cat_file = os.path.join(__package__, "data", F"{args.category}.txt")
    image_files = []
    gt_files = []

    with open(cat_file, 'r') as f:
        for line in f.readlines():
            file = line.strip()
            image_files.append(os.path.join(image_dir, file + ".jpg"))
            filename = file.split(".")[0]
            gt_files.append(os.path.join(gt_dir, filename + ".png"))

    n = len(image_files)

    ob_training_image_files = []
    ob_training_gt_files = []
    with open(os.path.join(__package__, "data", f"{args.category}_training_images.txt"), 'r') as f:
        for line in f.readlines():
            ob_training_img_file = os.path.join(image_dir, line.strip() + ".jpg")
            ob_training_gt_file = os.path.join(gt_dir, line.strip() + ".png")
            ob_training_image_files.append(ob_training_img_file)
            ob_training_gt_files.append(ob_training_gt_file)

    # show training instructions
    display_instructions(mywin, training_instruction(args.category))

    # run training experiments
    skip = False
    for i in range(10):
        ob_training_img_file = ob_training_image_files[i]
        ob_training_gt_file = ob_training_gt_files[i]

        with Image.open(ob_training_img_file) as img:
            original_width, original_height = img.size

        with Image.open(ob_training_gt_file) as gt:
            gt_ndarr = np.array(gt)
            gt = (gt_ndarr == INDEX).sum() / (original_width * original_height) * 100

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, (-NEW_IMG_WIDTH) // 2), height=NEW_IMG_WIDTH // 20)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, NEW_IMG_WIDTH // 2), height=NEW_IMG_WIDTH // 20)

        response = ''

        # Compute new dimensions while maintaining aspect ratio
        new_width = NEW_IMG_WIDTH
        aspect_ratio = original_width / original_height
        new_height = new_width / aspect_ratio

        # Create a visual stimulus for the image
        stimulus = visual.ImageStim(win=mywin, image=ob_training_img_file, size=(new_width, new_height))

        while True:  # Keep looping until they press 'enter'
            keys = event.getKeys()
            if 'escape' in keys:
                skip = True
                break

            if 'return' in keys:
                if response.isdigit() and int(response) >= 0 and int(response) <= 100:  # Check if the response is a positive integer
                    # Display the ground truth size of the image
                    ground_truth_text = visual.TextStim(win=mywin, text='', pos=(0, 0), height=NEW_IMG_WIDTH // 20)
                    ground_truth_text.setText(f"The correct size of the image is {gt:.1f}")
                    ground_truth_text.draw()
                    mywin.flip()
                    core.wait(3.5)
                    break
                else:  # If not a positive integer, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=NEW_IMG_WIDTH // 20, color='white')
                    prompt.setText("Please enter a positive integer within 100. Try again.")
                    prompt.draw()
                    mywin.flip()
                    core.wait(2)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                response += keys[0]  # Add the pressed key to the string

            input_text.setText("Your estimate: " + response)
            num_img_text.setText(f"image# {i + 1} / {10}")
            stimulus.draw()
            input_text.draw()
            num_img_text.draw()
            if args.assistance_tool == "grid":
                assistance_tool_grid(mywin, stimulus)
            elif args.assistance_tool == "circle":
                assistance_tool_circle(mywin, stimulus)
            else:
                raise NotImplementedError
            mywin.flip()

        if skip:
            break

    # show size estimation instructions
    display_instructions(mywin, estimation_instruction(args.category))

    # Check for saved state
    try:
        with open('saved_state.json', 'r') as f:
            saved_state = json.load(f)
            start_index = saved_state['current_index']
            responses = saved_state['responses']
            saved_elapsed_time = saved_state['elapsed_time']

            load_state = f"You have an unfinished experiment. If you want to continue the unfinished experiment from the #{start_index + 1} image " \
                         f"please press 'y', otherwise press 'n'."
            prompt = visual.TextStim(win=mywin, text=load_state, pos=(0, 0), height=NEW_IMG_WIDTH // 20, wrapWidth=NEW_IMG_WIDTH / 0.8, color='white')
            while True:
                prompt.draw()
                mywin.flip()
                keys = event.getKeys()
                if 'y' in keys:
                    break
                if 'n' in keys:
                    start_index = 0
                    responses = []
                    saved_elapsed_time = 0
                    break
    except FileNotFoundError:
        start_index = 0
        responses = []
        saved_elapsed_time = 0

    # Start the timer with the saved elapsed time
    experiment_timer = core.Clock()
    experiment_timer.addTime(saved_elapsed_time)  # Adjust the timer by adding the saved elapsed time

    for i in range(start_index, n):
        image_file = image_files[i]
        gt_file = gt_files[i]
        with Image.open(image_file) as img:
            original_width, original_height = img.size

        with Image.open(gt_file) as gt:
            gt_ndarr = np.array(gt)
            gt = (gt_ndarr == INDEX).sum() / (original_width * original_height) * 100

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, (-NEW_IMG_WIDTH) // 2), height=NEW_IMG_WIDTH // 20)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, NEW_IMG_WIDTH // 2), height=NEW_IMG_WIDTH // 20)

        # display the duration of time
        time_display = visual.TextStim(win=mywin, pos=(0, NEW_IMG_WIDTH // 1.6), color='white', height=NEW_IMG_WIDTH // 20)
        response = ''

        # Compute new dimensions while maintaining aspect ratio
        new_width = NEW_IMG_WIDTH
        aspect_ratio = original_width / original_height
        new_height = new_width / aspect_ratio

        # Create a visual stimulus for the image
        stimulus = visual.ImageStim(win=mywin, image=image_file, size=(new_width, new_height))

        while True:  # Keep looping until they press 'enter'
            # keep displaying the elapsed time and listening for the key.
            elapsed_time = experiment_timer.getTime()
            time_display.text = f"Elapsed Time: {elapsed_time:.0f} seconds"

            keys = event.getKeys()
            if 'escape' in keys:
                # Save the state
                with open('saved_state.json', 'w') as f:
                    elapsed_time = experiment_timer.getTime()
                    json.dump({'current_index': i, 'responses': responses, 'elapsed_time': elapsed_time}, f)
                mywin.close()
                core.quit()

            if 'return' in keys:
                if response.isdigit() and int(response) >= 0 and int(response) <= 100:  # Check if the response is a positive integer
                    break
                else:  # If not a positive integer, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=NEW_IMG_WIDTH // 20, color='white')
                    prompt.setText("Please enter a positive integer within 100. Try again.")
                    prompt.draw()
                    mywin.flip()
                    core.wait(2)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                response += keys[0]  # Add the pressed key to the string

            input_text.setText("Your estimate: " + response)
            num_img_text.setText(f"image# {i + 1} / {n}")
            stimulus.draw()
            time_display.draw()
            input_text.draw()
            num_img_text.draw()
            if args.assistance_tool == "grid":
                assistance_tool_grid(mywin, stimulus)
            elif args.assistance_tool == "circle":
                assistance_tool_circle(mywin, stimulus)
            else:
                raise NotImplementedError
            mywin.flip()

        responses.append((image_file.split(os.sep)[-1], response, f"{gt:.1f}"))

    with open(args.result_file + ".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image File', 'Response', 'GT'])  # Writing header
        for row in responses:
            writer.writerow(row)

    mywin.close()


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


def display_instructions(window, instruction):
    # Display a prompt above the image
    prompt = visual.TextStim(win=window, text=instruction, pos=(0, 0), height=NEW_IMG_WIDTH // 20, wrapWidth=NEW_IMG_WIDTH / 0.8, color='white')

    # Draw the prompt
    while True:
        prompt.draw()
        window.flip()
        keys = event.getKeys()
        if 'return' in keys:
            break


if __name__ == "__main__":
    main()
