#Bird policy generator

This program main purposes is to create a preference file
for the bird daemon to replicate Fabrikant policies on
a given topology.

The output file is in bird style and can be given as input
to the conf file generator.

### Requirements
* argparse
* networkx

The graphml should be formatted in the correct IoF standard way

### How to use it

use the main options given by the program:

* -w, --write-to WRITETO, Output conf file where the configuration will be
                        written
* -g, --graph GRAPH, graph file to use [MANDATORY]
* -o, --outer signal the presence of inner nodes

An example command could be:

`python3 gen_bird_preferences.py --graph small_g.graphml`

This command will generate automatically the pref.conf file for this "small_g.graphml" graph