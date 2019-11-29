Internet on FIRE BGP py simulator
===

## Intro

This is a python simulator for BGP, and the main purpose of this simulator 
is to reproduce the results presented in the [Fabrikant paper
](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=5935139)

## Execution

A general fabrikant graphml file needs to be provided to the simulator to replicate the environment.

A general fabrikant graphml could be produced with the script in the `topos` folder with the following command:

`python3 topos/genFABREXfig1.py`

It will produce the file `test.graphml` that can be used to create a simulation.

Now is possible to run a simulation with the command:

`python3 bgpSimulator.py -g test.graphml -w outputDir`

Pay attention, the output dir must exist, in case you did not create it you can 
use the command `mkdir outputDir`

Now in the output directory you will find the simulation files produced by the environment.

A more deep explanation of the simulator is available in the `bgpSim_documentation` folder

## Repeated execution

For simplicity to execute more experiments on the same topology is possible to use 
the bash file provided, it's called `nSimulations.bash` it only needs the number of 
simulations to repeat, the graph file and the output dire, follow this example:

`./nSimulations.bash 50 test.graphml outDir`

Obviously the output dir must exist. 