# size-estimation-experiment
A labeling tool to label the size of objects in PASCAL VOC dataset.

### Dataset
dataset can be download from [here](https://uofwaterloo-my.sharepoint.com/:f:/r/personal/x44fan_uwaterloo_ca/Documents/target-size/pascal?csf=1&web=1&e=ZWH7OY)
### Tested environment on macOS and Windows
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
python3 -m xvolume -dp <your dataset path (to VOC2012 folder)> -c dog  # run dog class
```

options:

`dp` path to PASCAL dataset on your local system. 

`category` indicates the class in Pascal dataset, you can choose from 

`'aeroplane', 'bicycle', 'bird', 'boat','bottle', 'bus', 'car', 'cat', 'chair','cow', 'diningtable', 'dog', 'horse','motorbike', 'person', 'pottedplant','sheep', 'sofa', 'train', 'tvmonitor', 'test'`

`window-size` sets the window size of the program (default 1200,900). If the window is too large, try 800,600

e.g.

```bash
python3 -m xvolume -dp .../VOC2012/ -c dog --window-size 800,600
```

`result-file` sets the file name of the experimental results (default is `responses`)

e.g.
```bash
python3 -m xvolume -dp .../VOC2012/ -c dog --result-file output  # no extension, '.csv' will be appended to the file name
```


`assistance-tool` sets the assistance tool for size estimation experiments. You can choose from `grid` or `absbox`

- absbox: boxes of absolute size, size of each box is the same across the dataset. 
- grid: 20 boxes, each signifies 5% of the volume

e.g.
```bash
python3 -m xvolume -dp .../VOC2012/ -c dog --assistance-tool grid # default is absbox
```

`unit` sets the input unit (percent or boxes). When using absbox as assistance tool, only unit `boxes` is available

e.g.
```bash
python3 -m xvolume -dp .../VOC2012/ -c dog --unit percent  # default is boxes
```

You can also check descriptions of options with help command
```bash
python3 -m xvolume --help
```

### Test the tool is working 
Highly recommend you check the tool has been set up properly (intermediate and final experimental results are saved) before running the whole experiment (whole experiment may take hours to finish)

Run the following command (multiple times). It provides a short experiment: 10 training images + 5 real experiment images
```bash
python3 -m xvolume -dp .../VOC2012/  -c test
```

Here is a checklist you can use to verify the tool is working properly:

- [ ] After you finished the short experiment, you can see experimental results stored in a csv file in `results` folder (Default is responses.csv. Use option `--result-file` or `-f` to set the file name)
- [ ] If you quit in the middle, you can see a json file named `<class>_saved_state.json` in the `states` folder storing intermediate results
- [ ] If you resume and finish the experiment, you can see experimental results stored in a csv file in `results` folder. 

### How to use the tool
After running the above command in your terminal, a window will pop up and display the instructions. Press `Enter` key on your keyboard to continue. For training phase, you can skip by pressing `Esc` key on your keyboard when you see a training image. It shows another instructions for the real experiment.
Press `Enter` key to run the experiment. You can only enter positive numbers. After you put the number, press `Enter` to jump to the next image. When you want to have a break, press `Esc` to quit the experiment. Next time you can resume from where you end by pressing `y` when it asks whether you 
want to resume your previous unfinished experiment. Otherwise, press `n`.

### Experimental results
It's highly recommended that you define the name of experimental result file with option `-f <your result file name>` when you run the experiment.
The default result file name is `responses`. If you use the same name and run the experiment twice, the first file will be **overwritten and deleted**.
Result files are saved in the `results` folder. Intermediate results are saved in a json file in the `states` folder.  
