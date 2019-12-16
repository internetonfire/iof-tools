# Parser from bird log files to CSV

This program is a parser for log file formatted in a certain way from our version of bird to CSV files.

Our implementation of Bird use the FATAL log level (that was not used) to log some message information.

###Requirements

This software requires the following libraries:

* argparse
* os
* progressbar
* pandas
* datetime

you can use pip3 to install all of them 

###Usage

The software requires a log input and a csv output.

An example could be:
`python3 logReader.py -ff ../logs/ -oo ../logsToCSV/`

This command will take as input a folder named `logs` with different logs folders with all the file logs and will produce a folder
`logsToCSV` that contains all the CSV files, one for each logged experiment.

The possible arguments of the parser are the following:

* -f, --folder [path to the folder] it defines an experiment folder where are stored a bunch of logs files
* -ff, --folders [path to the folder of folders] it defines a folder with more experiments folders
* -o, --out [csv output file] it defines the output file
* -oo, --outFolder [csv output folders] it defines where to store all the output files
* -w, --warnings it enables the warnings, by default it's true
* -nw, --no-warnings it disable the warnings

###Output

CSV files are the output of the software and them are formatted like it follows:

Columns:
* 'AS'
* 'TIME'
* 'TYPE'
* 'DEST'
* 'TO'
* 'FROM'
* 'NH'
* 'AS_PATH'
* 'PREVIOUS_BEST_PATH'
* 'ACTUAL_BEST_PATH'
* 'PROCESSING'