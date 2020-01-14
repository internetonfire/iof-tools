Internet on FIRE Scripts Repo
===

# ASSUMPTIONS

This `README` assumes that:
* you are working on a Unix-like system, so the variable `$HOME` is available;
* all the software will be in the `$HOME/src` folder;
* this repository has been cloned to `$HOME/src/iof-tools`;

Please execute the following beforehand:
```
mkdir -p $HOME/src
```

## Key pair setup

First of all, we assume that the user has a
valid [iMinds Authority account](https://authority.ilabt.iminds.be/). We also
assume that the user's public and private keys associated with the iMinds
Authority account are located in ~/.ssh/iminds.pub and ~/.ssh/iminds.key
respectively (the private key MUST NOT be encrypted).
If you don't have the keys already setup, you can follow these instructions:

Go to [iMinds Authority account management](https://authority.ilabt.iminds.be/getcert.php) and download your certificate
clicking on the "Download Login Certificate" button. Save it with the name `iminds.cert`.
Extract the public key with the following command:

`openssl x509 -pubkey -noout -in iminds.cert > ~/.ssh/iminds.pub`

Edit the`iminds.cert` file and copy the private key part in a new file named `iminds.protected.key`.

Remove the password from the private key:

`openssl rsa -in iminds.protected.key -out ~/.ssh/iminds.key`

## Omni tool

The [Omni](https://github.com/GENI-NSF/geni-tools/wiki/Omni) command line tool is
required to perform operations on the remote testbeds. Supported operations
include querying for testbed status/available resources, allocating/releasing
resources (slices) and creating/deleting experiments.

### Omni software dependencies

`omni` only works with Python version 2, so you should either switch your system
wide installation of Python to version 2 or install Python 2 and then change the
first line of the `omni` tool source code (see Omni installation).
On ubuntu, in order to install the `omni`'s software dependencies run the
following command:

```
sudo apt install python-m2crypto python-dateutil python-openssl libxmlsec1 
    xmlsec1 libxmlsec1-openssl libxmlsec1-dev autoconf
```

For other operating systems take a look at the official [wiki
page](https://github.com/GENI-NSF/geni-tools/wiki/QuickStart#debian--ubuntu)

### Omni installation

In order to install `omni` execute the following commands:

```
cd $HOME/src &&
git clone https://github.com/GENI-NSF/geni-tools omni &&
cd omni &&
./autogen.sh &&
./configure &&
make &&
make install 
```

If you are using Python version 3 and you don't want to switch system-wide to
Python 2, edit the first line of the `omni` source file and change it to
```
#!/usr/bin/env python2
```

Verify that `omni` has been installed correctly by executing `omni --version`.
This command should print something that resembles the following:

```
omni: GENI Omni Command Line Aggregate Manager Tool Version 2.11
Copyright (c) 2011-2016 Raytheon BBN Technologies
```

### Omni configuration file

The `omni_config` file provided in this repository is a template of the `omni`
configuration file. Before running any other `omni` command, this template file
must be modified in order to adapt it to the local host environment.


The users whose public keys will be installed on the testbed's nodes are listed
(comma separated list) in the value of the `users` key in the `omni` section.
For each user listed in the `users` key, there is a corresponding section (named
after the user name) containing the specific configuration for that particular
user. For example, in the current template configuration file one of the user
is `segata`, and the corresponding configuration section looks like this:

```
[segata]
urn = urn:publicid:IDN+wall2.ilabt.iminds.be+user+segata
keys = ~/.ssh/iminds.pub
```

The value of the field `keys` must be modified to point to the public key of the
user `segata`.

In case you need to add a new user, these are the required steps:
1. append the new user name in the comma separated list of the `users` key in
   the `omni` section.
2. add to the `omni_config` file a new section for the new user.
3. commit and push the new `omni_config` template.

# Testbed resource reservation
You can use jFed directly to reserve nodes, if you plan on using a lot of nodes, you can use 
the rspec generation scripts to ease this step.

## RSPEC generation

RSPEC files (extension .rspec) are XML files that describes which nodes to
allocate in a given testbed. For the TWIST and w.iLab1 testbeds the .rspec files
can be generated automatically using the `gen-rspec.py` script. The script
supports the following command line parameters:

* `-t` (`--testbed`): specifies which testbed the RSPEC will be generated for.
  Use `twist` for the TWIST testbed, `wilab` for w.iLab1, `wall1` for
  VirtualWall1, and `wall2` for VirtualWall2. It is possible to specify a
  comma-separated list of testbeds, e.g. `wall1,wall2`.

* `-f` (`--filter`): comma separated list of node name prefixes. Only the
  available nodes whose name starts with one of the specified prefixes are
  inserted in the generated RSPEC. By default all the available nodes are
  used for generating the RSPEC file.

* `-n` (`--nodes`): comma separated list of node names. Only the available nodes
  whose name is listed with the `-n` option are inserted in the RSPEC file. By
  default all the available nodes are used. The `-n` option takes precedence
  over `-f`.

* `-w` (`--hardware`): comma separated list of hardware types (e.g.,
  `pcgen05`). To know the type of hardware, look inside the [Virtual Walls
  webpage](https://doc.ilabt.imec.be/ilabt/virtualwall/hardware.html) or
  inside jFed.

For example, an RSPEC containing all the available nodes in the TWIST testbed
can be generated with the following command:

```
./gen-rspec.py -t twist > twist_all.rspec
```

Instead, an RSPEC containing all the nuc nodes in the TWIST testbed can be
generated with the following command:

```
./gen-rspec.py -t twist -f nuc > twist_nuc.rspec
```

An RSPEC containing only nuc4 and nuc6 from the TWIST testbed can be
generated with the following command:

```
./gen-rspec.py -t twist -n nuc4,nuc6 > twist_nuc_4_6.rspec
```

An RSPEC containing nodes of hardware type `pcgen05` from both the
VirtualWall1 and the VirtualWall2 testbeds can be generated with the following
command:

```
./gen-rspec.py -t wall1,wall2 -w pcgen05 > iof.rspec
```

Note that, in any case, a node is inserted in the RSPEC only if it is available
in the moment the `gen-rspec.py` command is executed. For this reason the
suggested best practice is to execute `gen-rspec.py` just before allocating the
resources using the `reserve.py` command.

## Reserving resources

One simple way of reserving the resource is to open the generated `.rspec`
file inside jFed and click on `Run`. This is also the safest option as the
`reserve.py` script is still under development.

The `reserve.py` command can be used to allocate nodes specified in an `.rspec`
file and to release resources previously allocated. The command supports the
following parameters:

* `-t` (`--testbed`): specifies in which testbed to allocate the nodes. The
  testbed specified here must match the testbed used in the .rspec file
  specified with the parameter `-f`. Use twist for the TWIST testbed and wilab
  for w.iLab1;

* `-d` (`--duration`): it's an integer value that specifies how many hours the
  nodes will be reserved for. The minimum value currently supported is 3.

* `-s` (`--name`): specifies the name that identify the experiment. Every
  experiment whose allocation time overlaps must have a unique name.

* `-f` (`--rspec`): specifies the path to the .rspec file generated with the
  `gen-rspec.py` command.

* `-p` (`--project`): specifies the project the experiments belongs to (by
default `internetonfire`).

By default `reserve.py` allocate the resources specified in the .rspec file. The
same command can be used also to release previously allocated resources using
the `-r` (`--release`) parameter.

For example, an experiment called `iofexp1` that allocates in the Wall1
testbed the nodes specified in the file `iof.rspec` for 4 hours can be
created with the following command:

```
./reserve.py -t wall1 -d 4 -n iofexp1 -f iof.rspec
```

Instead, the resources allocated in `iofexp1` can be released with the
following command:

```
./reserve.py -t wall1 -d 4 -n iofexp1 -f iof.rspec -r
```

The command queries for the status of the testbed every 10 seconds, and reports
when everything is up and running.

**WARNING:** the `reserve.py` script currently works only when a single
testbed is involved. In case of an `.rspec` files with nodes from multiple
testbeds, the operations needs to be performed twice. This is under development.

## Generating SSH and Ansible config

After generating the `rspec` file, the `gen-config.py` script can generate
the SSH and the ansible configuration files to access the nodes of the
testbeds. To do so, simply run:

```
./gen-config.py -r <rspec files> -u <username> -k <identity file>
```

The identity file is the private key or the certificate obtained after getting
an account from the [iMinds authority](https://authority.ilabt.iminds.be/).
This file will be copied under the current directory with the name `id.cert`. The 
username is your username on the Testbed.

The script will generate:
* `ssh-config`: the configuration file to be given to the SSH command (e.g.,
  `ssh -F ssh-config ...`). This defines the names of the hosts as `node<i>`,
  for `i` going from 0 to N-1. To connect to one host, you can thus run
  `ssh -F ssh-config node0`. To connect to the node, the configuration uses a
  proxy node with public IP address, which is called `proxy0`.
* `ssh-config-no-proxy`: the same configuration file as `ssh-config` but
  without the `ProxyCommand` through `proxy0`. This can be used by `ansible`
  when run on a testbed node.
* `ansible.cfg`: the Ansible configuration file.
* `ansible-hosts`: the Ansible inventory (list of nodes). In this file the
  group of nodes reserved for the experiments is named `nodes`. To test that
  this is properly working, try with `ansible nodes -m shell -a "uptime"`.

The filename of the configuration files can be changed via command line
arguments (see `./gen-config.py --help`).

## Setting up the testing environment on the nodes

The process of setting up the testing environment on the nodes is composed by two steps.
The first one takes care of installing all the needed software and tweaks some system parameters.
```
ansible-playbook playbooks/setup-nodes.yaml
```
from your local machine.

The second step is needed to configure the node0 as the master node for the experiments and
will correctly setup the syslog collection system on that node.
```
ansible-playbook playbooks/setup-syslog.yaml
```
on your local machine. If you want you can automate the whole procedure executing the `setup-nodes-environment.sh`
script.

To test the installation run from your local machine (do so only if you have
reserved a few nodes)
```
ansible nodes -m shell -a "~/iof-bird-daemon/bird --version"
```
The result should be the version of the bird daemon for each node in the
testbed.

## Retrieving CPU and network info

To retrieve CPU and interface information for all the nodes in the testbed run
```
./get-node-info.sh
```
This will create a `cpu_info` containing one `json` file
for each node in the testbed. The information can be used within python
programs using the `nodes_info::NodesInfo` class. See the unit test
`test_nodes_info.py` for an example usage.

If you used the `setup-nodes-environment.sh` in the previous step, the informations have already
been retrieved by the script. If you want to do it by hand, be sure to delete the `cpu_info` directory first.

# Topologies and BGP configurations

This section describes the tools that are used to generate network topologies
to test and the corresponding `bird` configuration files.

## Chain gadget topology

This tool generates *chain gadget* topologies as described in the Fabrikant
and Rexford paper *There's something about MRAI: Timing diversity can
exponentially worsen BGP convergence*. The tool is composed by two files
* `chain_gadget.py`: main library that exposes the `gen_chain_gadget` method.
* `gen_chain_gadget.py`: script that invokes the `gen_chain_gadget` method of
 the library and writes the graph on a `.graphml` output file.

The parameters that both the method accepts as inputs are the following (the
parameters of the script have different names, but the same meaning):
* `n_rings`: the number of rings to generate in the topology. For example,
 the number of rings in Figs. 1 and 3 in the paper is 3. The rings connected
 together form the chain.
* `n_inner`: the number of inner nodes. Each ring as inner nodes (marked with
 `Y_i` in the paper). The topology in Fig. 1 in the paper has only 1 inner
 node per ring, while Fig. 3 has 3.
* `add_outer`: if set to `true`, the tool will generate outer nodes as well
 (nodes marked with `Z_i` in the paper). The topology in Fig. 1 in the paper
 has no outer nodes, while Fig. 3 has 4. The number of outer nodes is
 automatically derived, and it is simply the number of inner nodes plus 1.
* `node_type`: the node type to assign to nodes. This can either be `T`, `M`,
 `CP`, or `C`.
* `edge_type`: the edge type to assign to edges. This can either be `transit` or
 `peer`. By default this is set to `transit`.
* `set_timer`: if set to `true`, the tool will compute the `MRAI` timer for
 the nodes, so that the automatic BGP configuration tool can use them during
 the generation phase. The timer is assigned with an exponentially decreasing
 value, starting with the default of `30 s`. The left-most ring (according to
 the graphical description of the topology in the paper) has the highest
 timer. Each ring's timer is halved with respect to the one of its left ring.

As an example, if you want to generate an eight ring Fabrikant topology:

``
cd graphGenerator/fabrikant &&
python3 gen_chain_gadget.py -r 8 -i 1 -t M -w OUTPUTFILE.graphml
``

## AS graph generator

 This [tool](https://github.com/lucabaldesi/AS_graph_generator) generates graphs
resembling the Internet BGP speaker topology.

Generation is as easy as typing:

``
python3 generate.py <number_of_nodes> <number_of_graphs>
``
## Adding multiple destinations on the topology

If you plan to experiment on Elmokashfi graphs or you want to correctly calculate the DPC value for the nodes, you'll need
to have all the nodes exporting a destination. In the *utils* folder you'll find a small tool you can use to add
destinations to a graph. Actually it adds a single destination to every non-tier1 node. You can use it as follows:

``
cd utils &&
python3 gen-destinations.py -g <input-graph> -o <output-graph>
``

In order to correctly set the DPC MRAI values, this step **MUST** be done before using the MRAI Setter tool.

## MRAI Setter
This tool sets the MRAI value on a graphml topology, using a specific strategy. You can look
at the Readme file in the `mrai_setter` folder for a complete explanation of the arguments.

## Bird Policy file generator
If you want to simulate a chain gadget topology you must also generate a Bird policy file.
This generator implements the routing policies needed on for the correct functioning of the Fabrikant topologies.
The policy generator will also add three nodes needed to manage the routing change in the
topology. **It is mandatory to have a single destination route to be announced configured in 
the graph.** If you have more than one (because you added them to correctly calculate the DPC values), you 
need to remove them by hand, editing the graphml file and deleting the "destination" entries
on every node (except the last one).
If you plan to use the Elmokashfi generator, you can skip this step.

To generate the policy file, use the tools as follows:

``
cd birdPolicyGenerator &&
python3 gen_bird_preferences.py -g <graph_name>
``

## Bird Config file generator
This tool is available in the `confFileGenerator` folder, it can be used to generate the Bird
configuration files to deploy on the Testbed. You can refer to the tool Readme for a complete explanation
of the different options.

## Custom modifications needed on Bird config files

#### AS_PATH prepending on Fabrikant topologies

If you plan to simulate a Fabrikant topology, some custom modification on the config must be made. In order to simulate the
change in the network we added three additional nodes, these nodes are in charge of managing the "d" destination. The nodes
are always identified as the three nodes with the highest number id. As an example, if you generated with the chain gadget generator
a 17 nodes topology, the nodes with id 0 to 16 are the nodes of the chain gadget and the nodes with id 17,18 and 19 are
in charge of managing the destination. The node exporting the destination is always the one with the highest id (in this case
the node with id 19). To simulate a change in the network we use the path prepending technique. For this reason, before
deploying the experiment you must enable the prepending on one of the links. In all our experiments we added the prepending
in the highest odd numbered node not announcing the route. In the example of the 17 nodes Fabrikant topology you'll need
to edit the bgp session file on node with id 17:

``
cd h_17/ && vim bgpSession_h_17_h_16.conf
``

In the section named filter *filter\_out\_h\_17\_h\_16* uncomment four of the six lines starting with *bgp_path.prepend*.

With this modification, the initial path preferred will be the one between node 16 and 18 ( AS 17 and 19 respectively),and 
this will be the link to be specified as the "broken" link (see section below for more details) with the command 
``./run-experiment.sh -a 19 -n 17``


#### Destinations removal on Elmokashfi topologies

Multiple destinations in Elmokashfi topologies are fully supported, but having a lot of destination routes will slow down
the first convergence phase (when the network topology is starting up). Depending on the number of nodes, if you don't remove
the destinations this step can take hours/days (as an example, a 4000nodes topology with 4000 destinations configured
is converging in around 37 hours using DPC MRAI settings). The best solution is to keep the destinations on the graph and have
them configured and ready to use in the Bird configuration files. Before we deploy the experiment we can easily comment
out the *export* command on all the Bird configuration files. With this method you can easily start up a simulation with
a single node exporting a destination (we always export a destination on the node generating the change in the network). With a
single destination exported, the network will usually converge in less than 5/10 minutes.

To comment out all the exported destinations you can use sed:

``
cd BIRD-CONFIG-FILES-DIR &&
sed -i -E 's/(^include  "bgpSessionExp.*)/#\1/' h_*/bgp_h_*.conf
`` 

You can then decide which node will trigger the change in the network, as an example if you decide to use the Autonomous System 100, you'll
need to uncomment the export session on that node (so it will correctly announce his route). **IMPORTANT NOTE** to remember: on
the graphml and on the Bird directory structure the Node ID is always the Autonomous System Number minus one (the graphml node
ids are starting from 0, while the AS0 does not exist) so if you want to have AS 100 announcing his route this is the
sed command to use:

``
cd BIRD-CONFIG-FILES-DIR && sed -i -E 's/(#)(include  "bgpSessionExp.*)/\2/' h_99/bgp_h_99.conf
``

After this modification, when you deploy the topology, the AS100 will start announcing his route.

# Experiment deployment and execution
To deploy an experiment on the Testbed, a mix of ansible playbooks and various scripts is needed.
You'll need:

* A set of nodes reserved on the Testbed
* The output directory of the Bird policy generator tool, containing the configuration files of the selected topology to be tested.
 
If you are testing a fabrikant gadget topology, only two nodes are needed. If you are testing an Elmokashfi topology, the total number
 of *cores* needed is dependant upon the number of Autonomous Systems of the topology.
 We tried topologies up to 4000 Autonomous Systems, using a 6:1 ratio (6 AS on a single core).
 
 
## Deployment of the topology
 
1. Copy the Bird config file directory in `~/src/iof-tools/`
2. You can use the `./deploy-experiment.sh` script to automate all the deployment steps.
 
 
## Running the experiment
After you successfully deployed the experiment files, you can connect to the control node to run the experiment: 
`ssh -F ssh-config node0`
From the control node, execute the `./run-experiment.sh` script. You'll need to specify some arguments:
 
1. `-a ASNumber` this flag specifies which AS is going to trigger the change in the topology
2. `-n ASNumber` this flag specifies the adjacency that will be changed, if you want to trigger the change on the AS 10 over the adjacency with the AS 15, the command line will be `-a 10 -n 15`. If you don't specify a neighbor, the first one will be selected.
3. `-r runs` this flag specifies the number of runs to execute, on each run the script will:
   * Start via ansible the bird process on all the nodes;
   * Check if all the bird processes and adjacencies are ok;
   * Wait for the topology to converge;
   * Trigger the change on the network;
   * Wait for the topology to converge;
   * Collect all the relevant logs;
   * Kill all Bird processes;
4. `-o outdir` output directory for the logs.

### Running multiple experiments

You can easily run the same topology (breaking the same link) using the `-r` flag on the `run-experiment.sh` script. This will
generate a single output directory with a subdirectory for every run. You can use this method to have the same experiment
running, as an example, 10 times, and then use the log parsing script to calculate the average convergence times.

#### Changing the "breaking" node

While on Fabrikant topologies changing how the network *breaks* does not make sense, on Elmokashfi topologies we can test the change
on the network from different nodes, to see how the topology behaves. Having to redeploy all the topology files to do this
kind of changes is very time consuming, so it's possible to do it directly on the testbed without having to redeploy a
new set of Bird configuration files.

To achieve this, some manual intervention is required. For every different type of "node break" you want to test, you need
to:

* Be sure that the Bird daemons have been killed;
* Modify the nodes export configuration (remember, the node triggering the change is the one exporting a destination);
* Restart the simulation, specifying the new AS of the node who will trigger the change.

As an example, let's suppose you ran an Elmokashfi topology and followed the instructions above, the first run has been done
with the AS100 announcing the route and triggering the change (so in the pre-deploy steps you modified with `sed` the AS100
configuration). Now let's do a new simulation, on the same topology but with a different triggering node (let's suppose as an
example the new triggering node will be AS200), the steps will be:

* Be sure that all the Bird processes have been killed;
* Change the AS100 configuration, removing the announce of the route;
* Change the AS200 configuration, adding the announce of the route;
* Run the new simulation, specifying the new "breaking" node and a new output dir.

To change the configuration of the Bird processes, you'll need to know on which node they are running. This information
can be retrieved from the *as.json* file, available in the node0 home directory and also in you local machine in *~/src/iof-tools*.
This file is generated by the deployment scripts and contains all the AS numbers and their relative running node in json format.

You can simply look at the file with `grep`:

* Locate the node where AS100 is running: `grep -A1 "\"as\": 100," as.json` the output of the command will contain the AS number
and the node in which it's running, in the form `"node": "nodeXX"`;
* Do the same thing for the AS200.

All these steps will be done on the Testbed:

* `ansible-playbook playbooks/kill-bird.yaml` This command will kill all the bird daemons;
* Now you need to connect to the node where AS100 is running and remove the announce of the route, you can do this step with
a single command: `ssh -F ssh-config nodeXX "sed -i -E 's/(^include  \"bgpSessionExp.*)/#\1/' iof-bird-daemon/nodes-config/h_99/bgp_h_*.conf"` The `nodeXX`
must be change to the correct node value obtained on the previous steps.
* Now you need to configure AS200 to announce his own route: `ssh -F ssh-config nodeYY "sed -i -E 's/(#)(include  \"bgpSessionExp.*)/\2/' iof-bird-daemon/nodes-config/h_199/bgp_h_*.conf"`
* Now you can launch a new set of simulations: `./run-experiment.sh -a 200 -r 5 -o RUN-AS200-BROKEN`

#### Getting random nodes to break

A simple utility is available in *utils/get\_random\_nodes.py* to extract random nodes with some specific characteristics. In our tests
we used this script to get the 10 different random nodes where the change on the network occurs. We wanted to reproduce a *worst case* scenario
so we extracted 10 random client "C" nodes, with a single BGP adjacency (this ensures that the change of path will be spread on all the nodes of the network) with
this command:

`python3 get_random_nodes.py -n 10 -t C -l -g GRAPHML-TOPOLOGY-FILE.graphml`


#### Running a different topology
If you plan to run a different topology (or the same topology with a different MRAI strategy), you'll need to redeploy the
experiment. You can use the same reserved resources on the Testbed but you must be sure to reset all the network configurations,
otherwise the new deploy will fail:

* Be sure all the Bird processes are stopped: `ansible-playbook playbooks/kill-bird.yaml`
* Reset the network namespace configuration: `ansible-playbook playbooks/clear-ns.yaml`
* Now you can deploy a new topology, using the `./deploy-experiment.sh` script

## Fetching the logs
The `fetch-results.sh` script can be used to fetch the logs from the testbed control node. If you are experimenting with 
a Fabrikant topology it will also clean the logs related to the nodes used to trigger the change in the network.

## Analysis of the logs

Once you have collected all the logs files you can analyze them with our tolls, we developed two versions of them
you can find both of them inside the `logHadlers` folder.

* logToCSV, this logger will convert all the logs files in a CSV that can be analyzed with other tools
* log_reader, this tool is used to produce an output that can be easily interpreted by our Gnuplot scripts

For both of this tools there is a complete README inside each one folder.

## Plot results

When you have translated your logs into CSVs or Gnuplot compatible files you can plot them with our scripts.
We developed some R scripts to interpret CSVs files and a Gnuplot script, both of them are in the folder `plotsGenerator`
and inside each folder there is a README.md file that explains how to use them with the input files.
