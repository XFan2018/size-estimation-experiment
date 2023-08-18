from psychopy import visual, core, event
import os
import csv


DATASET_PATH = "/Users/leo/Desktop/research/Pascal/"

def main():
    # Setup the Window
    mywin = visual.Window([800,600], monitor="testMonitor", units="deg")

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

    responses = []

    instruction = "Please estimate the size of the cat in the image as a percentage of the whole image. " \
                      "For instance, if you think the object occupies half the image, enter '50'. " \
                      "Please provide your estimate to the nearest whole number. Press 'Enter' to run the experiment"

    # Display a prompt above the image
    prompt = visual.TextStim(win=mywin, text=instruction, pos=(0, 0), height=0.6, wrapWidth=19, color='white')

    # Draw the prompt
    while True:
        prompt.draw()
        mywin.flip()
        keys = event.getKeys()
        if 'return' in keys:
            break

    for i, image_file in enumerate(image_files):
        if i > 10:
            break

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, -6), height=0.5)
        response = ''

        # Create a visual stimulus for the image
        stimulus = visual.ImageStim(win=mywin, image=image_file)

        while True:  # Keep looping until they press 'enter'
            keys = event.getKeys()

            if 'return' in keys:
                if response.isdigit() and int(response) >= 0 and int(response) <= 100:  # Check if the response is a positive integer
                    break
                else:  # If not a positive integer, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=0.5, color='white')
                    prompt.setText("Please enter a positive integer within 100. Try again.")
                    prompt.draw()
                    mywin.flip()
                    core.wait(2)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                response += keys[0]  # Add the pressed key to the string

            input_text.setText("Your estimate: " + response)
            stimulus.draw()
            input_text.draw()
            assistance_tool(mywin, stimulus, row=4, col=5)
            mywin.flip()


        responses.append((image_file.split(os.sep)[-1], response))

    with open('responses.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image File', 'Response'])  # Writing header
        for row in responses:
            writer.writerow(row)

    mywin.close()


def assistance_tool(mywin, stimulus, row, col):
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