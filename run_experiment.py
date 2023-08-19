from PIL import Image
from psychopy import visual, core, event
import os
import csv
import json
import argparse

parser = argparse.ArgumentParser("Size Estimation Experiment")
parser.add_argument("--dataset-path", "-dp", type=str, required=True, help="path to the Pascal dataset")
parser.add_argument("--window-size", '-ws', type=str, help="size of the display window, default is 1600,1200", default="1600,1200")
args = parser.parse_args()

DATASET_PATH = args.dataset_path  # "/Users/leo/Desktop/research/Pascal/"


def main():
    # Setup the Window
    mywin = visual.Window(list(map(int, args.window_size.split(","))), monitor="testMonitor", units="pix")

    # Check for saved state
    try:
        with open('saved_state.json', 'r') as f:
            saved_state = json.load(f)
            start_index = saved_state['current_index']
            responses = saved_state['responses']
            saved_elapsed_time = saved_state['elapsed_time']

            load_state = f"You have an unfinished experiment. If you want to continue the unfinished experiment from the #{start_index + 1} image " \
                         f"please press 'y', otherwise press 'n'."
            prompt = visual.TextStim(win=mywin, text=load_state, pos=(0, 0), height=30, wrapWidth=1000, color='white')
            while True:
                prompt.draw()
                mywin.flip()
                keys = event.getKeys()
                if 'y' in keys:
                    break
                if 'n' in keys:
                    start_index = 0
                    responses = []
                    saved_elapsed_time=0
                    break
    except FileNotFoundError:
        start_index = 0
        responses = []
        saved_elapsed_time = 0

    # Specify your image directory
    base_dir = DATASET_PATH
    dataset_dir = "VOCdevkit/VOC2012/"
    image_dir = os.path.join(base_dir, dataset_dir, "JPEGImages/")
    cat_file = os.path.join(base_dir, dataset_dir, "cat.txt")
    image_files = []

    with open(cat_file, 'r') as f:
        for line in f.readlines():
            file = line.strip()
            image_files.append(os.path.join(image_dir, file))

    n = len(image_files)

    instruction = "Please estimate the size of the cat in the image as a percentage of the whole image. " \
                      "For instance, if you think the object occupies half the image, enter '50'. " \
                      "Please provide your estimate to the nearest whole number. Press 'Enter' to run the experiment"

    # Display a prompt above the image
    prompt = visual.TextStim(win=mywin, text=instruction, pos=(0, 0), height=30, wrapWidth=1000, color='white')

    # Draw the prompt
    while True:
        prompt.draw()
        mywin.flip()
        keys = event.getKeys()
        if 'return' in keys:
            break

    # Start the timer with the saved elapsed time
    experiment_timer = core.Clock()
    experiment_timer.addTime(saved_elapsed_time)  # Adjust the timer by adding the saved elapsed time

    for i in range(start_index, n):
        image_file = image_files[i]
        if i >= 10:
            break

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, -500), height=30)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, 450), height=30)

        # display the duration of time
        time_display = visual.TextStim(win=mywin, pos=(0, 500), color='white', height=30)
        response = ''

        with Image.open(image_file) as img:
            original_width, original_height = img.size

        # Compute new dimensions while maintaining aspect ratio
        new_width = 800
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
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=20, color='white')
                    prompt.setText("Please enter a positive integer within 100. Try again.")
                    prompt.draw()
                    mywin.flip()
                    core.wait(2)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                response += keys[0]  # Add the pressed key to the string

            input_text.setText("Your estimate: " + response)
            num_img_text.setText(f"image# {i+1} / {n}")
            stimulus.draw()
            time_display.draw()
            input_text.draw()
            num_img_text.draw()
            assistance_tool_grid(mywin, stimulus, row=4, col=5)
            mywin.flip()


        responses.append((image_file.split(os.sep)[-1], response))

    with open('responses.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image File', 'Response'])  # Writing header
        for row in responses:
            writer.writerow(row)

    mywin.close()


def assistance_tool_grid(mywin, stimulus, row, col):
    # Draw a grid over the image
    image_width = stimulus.size[0]  # width of the image in pixels
    image_height = stimulus.size[1]  # height of the image in pixels

    # Calculate the distance between lines for the grid
    dx = image_width / col
    dy = image_height / row

    # Horizontal lines
    for i in range(row + 1):
        y_pos = i * dy - (image_height / 2)  # Adjusting position relative to the center of the image
        line = visual.Line(mywin, start=(-image_width / 2, y_pos), end=(image_width / 2, y_pos), lineColor='white')
        line.draw()

    # Vertical lines
    for i in range(col + 1):
        x_pos = i * dx - (image_width / 2)  # Adjusting position relative to the center of the image
        line = visual.Line(mywin, start=(x_pos, -image_height / 2), end=(x_pos, image_height / 2), lineColor='white')
        line.draw()




if __name__ == "__main__":
    main()