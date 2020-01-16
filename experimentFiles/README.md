# Experiment Files

In these directories you'll find all the configuration files needed to reproduce our experiments ready to be used.
What follow is a brief description of the structure of the directory tree:

--- 
The "fabrikant" directory contains all the files needed to reproduce the Fabrikant gadget topologies.
To reproduce this experiments you'll need two nodes on the Testbed.

fabrikant/graphml:
This directory contains all the graphml files of the topologies, the file name indicates the type of the
gadget and the mrai strategy implemented, the syntax is:
0_MRAISTRATEGY_fNUMBEROFNODES-dest_2.graphml
As an example, the file 0_dpc_f15n-dest_2.graphml is implementing a Fabrikant 15 nodes topology with the DPC mrai strategy.

fabrikant/bird-policy-files:
This directory contains all the policy files needed to correctly implement the routing strategy for the Fabrikant topologies.
Th syntax is:
0_MRAISTRATEGY_fNUMBERFONODES-dest-prefs.conf
As an example, the file 0_fabrikant_f11n-dest-prefs.conf relates to the Bird policy files needed to simulate
an 11 nodes fabrikant topology with the Fabrikant mrai strategy.

fabrikant/bird-config-files:
This directory contains the Bird configuration files, ready to be used for deployment on the Testbed. You can
skip all the graph generation and setup steps and copy one of these directories on your ~/src/iof-tools/ dir
in order to deploy the topology.
The syntax is:
0_MRAISTRATEGY_fNUMBEROFNODESn-dest/
As an example,the directory 0_30secs_f17n-dest contains all the configuration files needed to simulate a
fabrikant topology of 17 nodes with a standard 30seconds mrai strategy.

---

The "elmokashfi" directory contains all the files needed to reproduce the Elmokashfi simulations presented
on the paper. 
To reproduce this topology you'll need at least 700 cores on the Testbed.

elmokashfi/graphml:
This directory contains all the graphml files of the topology with two different mrai strategies, 30seconds
and DPC.

elmokashfi/bird-config-files.tgz
This tarball contains all the Bird configuration files, ready to be used for deployment on the Testbed. They
are presented in a compressed format due to the high number of files present. Before you can use them you need
to extract the files on the current directory and then copy the configuration directory you want to deploy
on your ~/src/iof-tools/ dir.


