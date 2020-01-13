## Gnuplot log plotter

This is a gnuplot script, the main purpose of this script is to plot the output of the 
log_parser.

Is possible to set this attribute from command line:
* outfile [arg], default='out.pdf', output file of the plotter
* inputfile [arg], default='logs.txt', input file where info are contained
* type [arg], default=1, if type is 0 the output will have less information
* timeRange [arg], default="[s]", Range of the time axes. uesd in the axes explanation
* yrng [arg], default=20, Range of the first y axes, it will start from 0
* y2rng [arg], default=20, Range of the second y axes, it will start from 0
* xmin [arg], default=0, where the x axes start, could be minus
* xmax [arg], default=70, x axes limit

Remember that the second y is in logscale
