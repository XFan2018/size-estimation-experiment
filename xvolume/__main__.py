import csv
import json
import os

from psychopy import core

from .class_mapping import Index
from .instructions import *
from .utils import *


def main():
    args = get_args()

    class_index = Index.get_index(args.category)

    window_width = int(args.window_size.split(",")[0])

    # Set up the Window
    assert "," in args.window_size and len(args.window_size.split(",")) == 2 and all([s.isdigit() for s in args.window_size.split(",")]), \
        "window size argument must be two positive integers separated by ',' representing the display window size."
    if args.assistance_tool == "absbox": assert args.unit == "boxes", "Input unit should be boxes if the assistance tool is absolute boxes"
    mywin = visual.Window(list(map(int, args.window_size.split(","))), monitor="testMonitor", units="pix")

    # initialize assistance tool
    assistance_tool = AssistanceTool(args.assistance_tool, mywin)

    # Specify your image directory
    base_dir = args.dataset_path
    image_dir = os.path.join(base_dir, "JPEGImages" + os.sep)
    gt_dir = os.path.join(base_dir, "SegmentationClassAug" + os.sep)

    category_file = os.path.join(__package__, "data", F"{args.category}.txt")
    image_files = []
    gt_files = []

    with open(category_file, 'r') as f:
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
    DisplayTool.display_instructions(mywin, training_instruction(args.category))

    # run training experiments
    skip = False
    training_responses = []
    training_gts = []
    for i in range(NUM_TRAINING_IMAGES):
        scale = Scale.SMALL

        ob_training_img_file = ob_training_image_files[i]
        ob_training_gt_file = ob_training_gt_files[i]

        with Image.open(ob_training_img_file) as img:
            original_width, original_height = img.size
            image_stimulus, new_width, new_height = ImageTool.resize_image(original_width, original_height, window_width, img)
            if args.assistance_tool == 'absbox':
                image_stimulus = ImageTool.pad_image(window_width, image_stimulus)

        with Image.open(ob_training_gt_file) as gt:
            gt_ndarr = np.array(gt)
            gt = (gt_ndarr == class_index).sum() / (original_width * original_height) * 100
            training_gts.append(float(gt))

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, (-window_width) // INPUT_TEXT_POSITION), height=window_width // IMAGE_FONT)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, window_width // INPUT_TEXT_POSITION), height=window_width // IMAGE_FONT)

        response = ''

        # Create a visual stimulus for the image
        stimulus = visual.ImageStim(win=mywin, image=image_stimulus, size=image_stimulus.size)
        user_input_done = False

        ground_truth_text = ""
        keys = []
        while True:  # Keep looping until they press 'enter'
            keys = event.getKeys()
            if 'escape' in keys:
                skip = True
                break

            if not user_input_done:
                if 'up' in keys:
                    scale = Scale.LARGE

                if 'down' in keys:
                    scale = Scale.SMALL

            if 'return' in keys:
                if VerificationTool.valid_input(response, args.unit, args.assistance_tool, new_width, new_height, scale,
                                                window_width):  # Check if the response is a float between 0 and 100
                    # Display the ground truth size of the image
                    if not user_input_done:
                        user_input_done = True

                        # Add response to the training_responses
                        size = ComputeTool.compute_size(response,
                                                        tool=args.assistance_tool,
                                                        unit=args.unit,
                                                        image_width=new_width,
                                                        image_height=new_height,
                                                        scale=scale,
                                                        window_width=window_width)
                        training_responses.append(float(size))

                        # set ground truth text
                        ground_truth_text = visual.TextStim(win=mywin, text='', pos=(0, (-window_width) / GROUND_TRUTH_TEXT_POSITION),
                                                            height=window_width // IMAGE_FONT)
                        ground_truth_text.setText(
                            ComputeTool.compute_ground_truth_image_size(gt, args.assistance_tool, args.unit, new_width, new_height, scale, window_width))
                        keys.pop()
                    else:
                        break
                else:  # If not a valid input, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=window_width // IMAGE_FONT, color=PROMPT_COLOR)
                    prompt.setText(VerificationTool.invalid_input_value(args.unit, args.assistance_tool, new_width, new_height, scale, window_width))
                    prompt.draw()
                    mywin.flip()
                    core.wait(INVALID_INPUT_DISPLAY_TIME)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0:
                if not user_input_done and VerificationTool.is_digit_or_dot(keys[0]):  # if the ground truth size is not shown, add keys to the response
                    if keys[0] == "period":
                        response += '.'
                    else:
                        response += keys[0]  # Add the pressed key to the string

            input_text.setText("Your estimate: " + response)
            num_img_text.setText(f"image# {i + 1} / {NUM_TRAINING_IMAGES}")
            stimulus.draw()
            input_text.draw()
            num_img_text.draw()
            if user_input_done:
                ground_truth_text.draw()
            assistance_tool(stimulus, scale)
            mywin.flip()

        if skip:
            break
    # show statistics of experimental results
    if not skip:
        avg = StatisticsTool.training_experimental_results_statistics(training_responses, training_gts)
        DisplayTool.display_training_statistics(mywin, avg)

    # show size estimation instructions
    DisplayTool.display_instructions(mywin, estimation_instruction(args.category))

    # Check for saved state
    try:
        with open(os.path.join("states", f'{args.category}_saved_state.json'), 'r') as f:
            saved_state = json.load(f)
            start_index = saved_state['current_index']
            responses = saved_state['responses']
            saved_elapsed_time = saved_state['elapsed_time']

            load_state = f"You have an UNFINISHED experiment! \n\n 1. Press Y to continue the unfinished experiment from the #{start_index + 1} image. " \
                         f"\n 2. Press N to start a new experiment and your previous intermediate results may be deleted!"
            prompt = visual.TextStim(win=mywin, text=load_state, pos=(0, 0), height=window_width // IMAGE_FONT, wrapWidth=window_width / INSTRUCTION_WIDTH,
                                     color=PROMPT_COLOR)
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
        scale = Scale.SMALL
        start_time = experiment_timer.getTime()
        image_file = image_files[i]
        gt_file = gt_files[i]
        with Image.open(image_file) as img:
            original_width, original_height = img.size
            image_stimulus, new_width, new_height = ImageTool.resize_image(original_width, original_height, window_width, img)
            if args.assistance_tool == 'absbox':
                image_stimulus = ImageTool.pad_image(window_width, image_stimulus)

        with Image.open(gt_file) as gt:
            gt_ndarr = np.array(gt)
            gt = (gt_ndarr == class_index).sum() / (original_width * original_height) * 100

        # Ask for the observer's estimate after the image is shown
        input_text = visual.TextStim(win=mywin, text='', pos=(0, (-window_width) / INPUT_TEXT_POSITION), height=window_width // IMAGE_FONT)

        # display the number of image
        num_img_text = visual.TextStim(win=mywin, text='', pos=(0, window_width / IMAGE_NUMBER_TEXT_POSITION), height=window_width // IMAGE_FONT)

        # display the duration of time
        time_display = visual.TextStim(win=mywin, pos=(0, window_width / TIME_TEXT_POSITION), color=PROMPT_COLOR, height=window_width // IMAGE_FONT)
        response = ''

        # Create a visual stimulus for the image
        stimulus = visual.ImageStim(win=mywin, image=image_stimulus, size=image_stimulus.size)

        while True:  # Keep looping until they press 'enter'
            # keep displaying the elapsed time and listening for the key.
            elapsed_time = experiment_timer.getTime()
            time_display.text = f"Elapsed Time: {elapsed_time:.0f} seconds"

            keys = event.getKeys()
            if 'escape' in keys:
                # Save the state
                with open(os.path.join("states", f'{args.category}_saved_state.json'), 'w') as f:
                    elapsed_time = experiment_timer.getTime()
                    json.dump({'current_index': i, 'responses': responses, 'elapsed_time': elapsed_time}, f)
                mywin.close()
                core.quit()

            if 'up' in keys:
                scale = Scale.LARGE

            if 'down' in keys:
                scale = Scale.SMALL

            if 'return' in keys:
                if VerificationTool.valid_input(response, args.unit, args.assistance_tool, new_width, new_height, scale, window_width):
                    break
                else:  # If not a valid input, prompt the observer and reset the response
                    response = ''
                    prompt = visual.TextStim(win=mywin, pos=(0, 0), height=window_width // IMAGE_FONT, color=PROMPT_COLOR)
                    prompt.setText(VerificationTool.invalid_input_value(args.unit, args.assistance_tool, new_width, new_height, scale, window_width))
                    prompt.draw()
                    mywin.flip()
                    core.wait(INVALID_INPUT_DISPLAY_TIME)

            elif 'backspace' in keys:
                response = response[:-1]  # Remove the last character
            elif len(keys) > 0 and VerificationTool.is_digit_or_dot(keys[0]):
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
            assistance_tool(stimulus, scale)
            mywin.flip()

        size = ComputeTool.compute_size(response,
                                        tool=args.assistance_tool,
                                        unit=args.unit,
                                        image_width=new_width,
                                        image_height=new_height,
                                        scale=scale,
                                        window_width=window_width)
        end_time = experiment_timer.getTime()
        time = end_time - start_time
        responses.append((image_file.split(os.sep)[-1], size, f"{gt:.2f}", f"{time:.1f}"))

    with open(os.path.join("results", args.result_file) + ".csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Image File', 'Response', 'GT', 'Time'])  # Writing header
        for row in responses:
            writer.writerow(row)

    avg_error, total_time = StatisticsTool.experimental_results_statistics(responses)
    DisplayTool.display_final_statistics(mywin, avg_error, total_time)
    mywin.close()


if __name__ == "__main__":
    main()
