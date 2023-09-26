# size-estimation-experiment
A tool for subjects to estimate the size of objects in PASCAL VOC dataset.

### Dataset
dataset can be download from [here](https://uofwaterloo-my.sharepoint.com/:f:/r/personal/x44fan_uwaterloo_ca/Documents/target-size/pascal?csf=1&web=1&e=ZWH7OY)
### tested environment on macOS
| software   | versions |
|------------|----------|
| Python     | 3.10.12  |
| pip        | 23.2.1   |
| setuptools | 68.2.2   |


### Run experiment
```bash
git clone https://github.com/XFan2018/size-estimation-experiment.git
cd size-estimation-experiment
pip install -r requirements.txt
python3 -m pascal-size-estimate -dp <your dataset path (to VOC2012 folder)> -c dog  # run dog class
```

options:

`dp` path to PASCAL dataset on local system. 

`category` indicates the class in Pascal dataset

`window-size` sets the window size of the program (default 1600,800). If window is too large, try 800,600

e.g.

```bash
python3 -m pascal-size-estimate -dp .../VOC2012/ -c dog --window-size 800,600
```

`result-file` sets the file name of the experimental results

e.g.
```bash
python3 -m pascal-size-estimate -dp .../VOC2012/ -c dog --result-file output  # no extension, '.csv' will be appended to the file name
```


`assistance-tool` sets the assistance tool for size estimation experiments. You can choose from `grid` or `circle`

e.g.
```bash
python3 -m pascal-size-estimate -dp .../VOC2012/ -c dog assistance-tool circle # default is grid
```

You can also check descriptions of options with help command
```bash
python3 -m pascal-size-estimate --help
```

### test the tool is working 
It's highly recommend you check the tool has been set up properly (intermediate and final experimental results are saved) before running the whole experiment (whole experiment may take hours to finish)

Run the following command (multiple times). It provides a short experiment: 10 training images + 5 real experiment images
```bash
python3 -m pascal-size-estimate -dp .../VOC2012/  -c test
```

Here is a checklist you can use to verify if the tool is working properly:

- [ ] After you finished the short experiment, you can see experimental results stored in a csv file (Default is responses.csv. Use option --result-file to set other names)
- [ ] If you quit in the middle, you can see a json file named `saved_state.json` storing intermediate results
- [ ] If you resume the experiment, when the experiment is done, you can see experimental results stored in a csv file. 

### how to use the tool
After running the above command in your terminal, a window will pop up and display the instructions. Press `Enter` key on your keyboard to continue. For training phase, you can skip by pressing `Esc` key on your keyboard when you see a training image. It shows another instructions for the real experiment.
Press `Enter` key to run the experiment. You can only enter positive integers from 0 to 100. After you enter the number, press `Enter` to jump to the next image. When you want to have a break, press `Esc` to quit the experiment. Next time you can resume from where you end by pressing `y` when it asks whether you 
want to resume your previous unfinished experiment. Otherwise press `n`.
