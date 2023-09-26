# size-estimation-experiment

### Prerequisite
Python 3.10 
### Instructions to run the experiment
```bash
cd size-estimation-experiment
pip install -r requirements.txt
python3 run_experiment.py --category dog --window-size 800,600 --result-file output --assistance-tool grid
```
`category` indicates the class in Pascal dataset

`window-size` sets the window size of the program

`result-file` sets the file name of the experimental results

`assistance-tool` sets the assistance tool for size estimation experiments. You can choose from `grid` or `circle`
