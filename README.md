# ChemBO
## System requirements
### Dependencies
A compiled version of the ChemBO GUI is available for MacOS [here](https://github.com/johnfhartwig/ChemBO/raw/master/chembo.dmg).
This version was compiled on MacOS 10.15.1, though it should be compatible with previous versions of MacOS as well.
A full list of requirements and dependencies is available in `environment.yml`.

## Installation guide
To compile ChemBO and/or run tests to reproduce the results we show, please install [MiniConda](https://docs.conda.io/en/latest/miniconda.html) and run the following commands from the ChemBO directory:
```
conda env create -f environment.yml
conda activate chembo
```
Before compiling, please check that ChemBO works by running
```
python chembo.py
```
If the ChemBO window pops up, you're good to go! To compile ChemBO on MacOS, run:
```
make
```
The compilation process should take around 3-5 minutes.

## Demo/Testing
To run ChemBO with the datasets we show, run test.py with different commands. For example, to test our results on the Doyle C-N coupling dataset, run the command:
```
python test.py -c tests/cbo/doyle.cbo -d tests/data/doyle/doyle.npy
```
To stop the calculation after hitting a certain target, use the `-t` flag. For example, to stop the Doyle dataset optimization after reaching 90% yield, run the command:
```
python test.py -c tests/cbo/doyle.cbo -d tests/data/doyle/doyle.npy -t 90
```

## Instructions for use
Upon opening ChemBO, the user is presented with this “splash screen”. The button labeled “New ChemBO project” opens the “New  ChemBO project” window, while the button labeled “Load ChemBO project” opens a file selection box, which allows a user to select an existing ChemBO project. Recently opened ChemBO projects are also visible through the “Recent ChemBO projects” pane, which can then be selected and opened by clicking the “Open” button.

The “New ChemBO project” window is used to set up new ChemBO projects. The user can specify a project name and a desired batch size with the text entry box and spinbox in the upper part of the window. The lower part of the window is used for viewing and making variables. The “Add…” button opens the “New variable” window, which allows a user to create a new variable. The “Edit…” button allows a user to edit an existing variable, while the “Delete” button allows a user to delete a variable. When the user is finished, clicking the “Done!” button will prompt the user to confirm their settings (they cannot be changed once the experiment begins.) before beginning the ChemBO experiment. The “Cancel” button prompts the user to confirm before closing the window and removing any variables created.

The “New variable…” window is used to create new ChemBO variables. There are three tabs which are used to select the type of connectivity a user desires.

For fully connected variables, possible variable values are added and removed with the “New value” and “Remove value” buttons, respectively. The name for each variable value can be edited by double clicking on the value in the list. Values can be reordered by simply dragging a value to the desired location.

For partially connected variables, groups are added and removed with the “New group” and “Remove group” buttons, respectively. While a group is selected, possible values within the group are added and removed with the “New value” and “Remove value” buttons, respectively.

For custom connected variables, a path to an adjacency matrix (as a numpy .npy file) should be specified with the “Browse…” button, which opens a file browser dialog box for the user to select a file. When creating a new variable, the names of each vertex described by the adjacency matrix should be specified by double clicking the corresponding entry in the names list.

To finish setting up a variable, the user presses the “Done!” button. To exit out without saving changes, the user presses the “Cancel” button.

The “main window” of ChemBO is the interface for the user to run the experiment. The name of the experiment is given in the upper left corner, with a status bar indicating the optimization progress. The number of recommended experiments is calculated automatically by computing the minimum number of experiments (which is a multiple of the batch size) required to match the greedy algorithm. The best value observed so far, as well as the combination which obtained it, is indicated in the upper right corner. The full log of reactions inputted into ChemBO can be viewed by clicking the “View log” button. A list of variables is visible on the left (for the user’s reference), and the next set of experiments is given on the right. The user enters the next value into the appropriate “Value” box and hits the “Submit” button to generate the next batch of experiments. While it is possible to omit a value from the next batch of experiments, we highly recommend against doing this if possible because this induces a bias into future experiments.

