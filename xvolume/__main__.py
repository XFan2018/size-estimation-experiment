import argparse
import csv
import json
import os
from .class_mapping import Index
import numpy as np
from PIL import Image
from psychopy import core

from .instructions import *
from .utils import *
from .constants import *


def main():
    args = get_args()
    class_index = Index.get_index(args.category)
    img_width = int(args.window_size.split(",")[0]) // 2

    # Setup the Window
    assert "," in args.window_size and len(args.window_size.split(",")) == 2 and all([s.isdigit() for s in args.window_size.split(",")]), \
        "window size argument must be two positive integers separated by ',' representing the display window size."

    mywin = visual.Window(list(map(int, args.window_size.split(","))), monitor="testMonitor", units="pix")

    # Specify your image directory
    base_dir = args.dataset_path
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
            gt = (gt_ndarr == class_index).sum() / (original_width * original_height) * 100

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, (-img_width) // 2), height=img_width // 20)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, img_width // 2), height=img_width // 20)

        response = ''

        # Compute new dimensions while maintaining aspect ratio
        new_width = img_width
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
                if valid_input(response):  # Check if the response is a float between 0 and 100
                    # Display the ground truth size of the image
                    ground_truth_text = visual.TextStim(win=mywin, text='', pos=(0, 0), height=img_width // 20)
                    ground_truth_text.setText(ground_truth_image_size(gt))
                    ground_truth_text.draw()
                    mywin.flip()
                    core.wait(GT_VALUE_DISPLAY_TIME)
                    break
                else:  # If not a valid input, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=img_width // 20, color=PROMPT_COLOR)
                    prompt.setText(invalid_input_value())
                    prompt.draw()
                    mywin.flip()
                    core.wait(INVALID_INPUT_DISPLAY_TIME)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                if keys[0] == "period":
                    response += '.'
                else:
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
            prompt = visual.TextStim(win=mywin, text=load_state, pos=(0, 0), height=img_width // 20, wrapWidth=img_width / 0.8, color=PROMPT_COLOR)
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
            gt = (gt_ndarr == class_index).sum() / (original_width * original_height) * 100

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, (-img_width) // 2), height=img_width // 20)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, img_width // 2), height=img_width // 20)

        # display the duration of time
        time_display = visual.TextStim(win=mywin, pos=(0, img_width // 1.6), color=PROMPT_COLOR, height=img_width // 20)
        response = ''

        # Compute new dimensions while maintaining aspect ratio
        new_width = img_width
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
                if valid_input(response):
                    break
                else:  # If not a valid input, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=img_width // 20, color=PROMPT_COLOR)
                    prompt.setText(invalid_input_value())
                    prompt.draw()
                    mywin.flip()
                    core.wait(INVALID_INPUT_DISPLAY_TIME)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                if keys[0] == "period":
                    response += '.'
                else:
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


if __name__ == "__main__":
    main()
