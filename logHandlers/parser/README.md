## Log parser

You can use this log parser to produce from the experiment folder fetched a file that
can be interpreted by the gnuplot plotter and with the sum-up of all the information.

### Read single experiment

You can use this script to get the information about just one experiment.
For example if the logs files of the experiments are in the folder: `iof-tools/Experiemnt1/logs/*`
You can use the following command to read them:

`python3 log_parser.py -f ../../RESULTS/run1/logs/* > logs.txt`

The option -f describe where the logs files are contained

### Read the average of multiple experiemnts

Sometimes you have done more runs of the same experiment and you would like to plot
the average of all this runs, you can create the average file descriptor with the log_parser.
The constraint is that you pass a folder to the parser, it expect to find in this folder a list
of folders that represent all the experiments, and inside of each of them there are only the
logs files.

If we have a folder with different runs at the following path: `iof-tools/fabr10runs/*`
you can use the following command:

`python log_parser.py -ff ../../fabr10runs/ > average10runs.txt`

### Other arguments

There are some more arguments to have more information inside your plot:
* -c Compute convergence delay
* -t Compute the number of updates generated
* -T ['SECS', 'DSEC', 'CSEC', 'MSEC'], time resolution (s/decimal/cent/milli)
* -d [delta_value], use this value to set a negative delta value