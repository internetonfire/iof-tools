#Basic test

gen2 for now stable it uses `/30` networks for the point to point networks between nodes 

###Requirements

The requirement for this program is a well formed graph that respects the attribute specs, an internet 
graph could be generated with the software developed by Luca Baldesi, you can obtain it at it's 
[repository](https://github.com/AdvancedNetworkingSystems/AS_graph_generator/tree/undirected).

But for what I know while I'm writing this README sooner or later this graph generator should be imported 
in the major release of Netowrkx.

Are also required the following python libraries:
* getopt
* os.path
* shutil
* sys
* ipaddress
* jinja2

###Test

launch the generator on a basic test:

`python3 confFileGen.py --graph small_g.graphml --out out/`

file `small_g.graphml` MUST exists and be well formed.

If the dir 'out/' does not exists it will be created.

Now inside the folder `out` you will find all the files needed to start the nodes.
And the scripts to configure the network for a specific node.

###Args
Mandatory args are: 
* --graph [file name]: name of the graphml (only graphml files are accepted) file that will be used to generate the conf files, this file needs to be correctly formatted and created. Only nodes of type 'C' generates routes. If this does not exists yet it will be created with a predefined number of nodes (20).
* --out [folder name]: folder where the conf files will be saved

Not mandatory args:
* --help, -h: show this help
* --directories: this arg does not require parameters, if present the output will be formatted to folders, for each bird node
* --nomrai: this option will override the mrai in the graphml file and preclude mrai commands to be in the conf file (To make the conf files compatibles with old bird daemons, by default bird does not implement MRAI, instead our implementation does)
* --mraitype [value]: define the type of mrai that will be used in the conf files, default is 0, 0 connection based, !0 destination based
* --prepath [value]: path used in front of all files (use the path where the conf files will be saved), default is "/etc/bird/"
* --ipnetworksgraph [attr_name]: defines the name of the attribute in the graphml file that represents the network address list that will be shared by a node, it needs to be a node attribute and since it's not possible to define a list inside a graphml attribute, network addresses should respect the following rule `[addr]/[netmask 8 to 24],[addr2]/[netmask], ecc`, **no checks are performed between networks**
* --noautomaticnetworks: if a C node has 0 networks defined with ipnetworksgraph or if ipnetworksgraph is not defined, an automatic network will be assigned to the node, with this param the automatic network will not be assigned, so a C could not share a network
* --doublepeering: if used this param will suppose to use a graphml file that have two edges for a peering relation, otherwise is supposed that the graphml have just one edge for the peering relation, and this edge will be used to create both relation files
* --fatallog: force the log to use only the FATAL set of errors
* --prefevaluator [pref_file]: is possible to define a preference evaluator, an example is given in prefExample.conf, if not defined no preferences will be injected into nodes
* --mraijitter [jitter]: jitter percentage that should be applied to timers, default is 25%.

Example command:

`python3 confFileGen.py --graph graph.graphml --out out/ --directories`

This command use the file graph.graphml to create configurations files.
Will be used the 'out' directory to save the files, and thanks to `--directories` all files will be moved to the corresponding directory. 
with this command will also be inserted the commands for mrai, to avoid this is possible to use the following command:

`python3 confFileGen.py --graph graph.graphml --out out/ --directories --nomrai`

###Graph restrictions
The following arguments are required to be formatted in the graphml file in the following way:

Nodes attributes:
* type: {T,M,C,CP}, which respectively indicates if a node is tier-1, mid-level, customer or content provider;
* destinations: [destination_string], it indicates the destinations exposed by the node.

Edge attributes:
* type: {transit, peer}, which for a couple of nodes (i, j), indicates whether there is a customer-provider or peer-to-peer relationship between i and j.
* customer: z node, in case the edge (i,j) type is transit, z identifies the customer among i,j (the relationship provider is hence the other node). It is set to 'none' in the case the edge type is not transit;
* termination1: i ∈ (i, j)
* termination2: j ∈ (i, j);
* mrai1: [interval] in seconds, it indicates the per link (i, j) minimum route ADV interval for node termination1. Note, node-based mrai setup (Fabrikant gadget) can be described by setting all its mrai edge intervals to the same value.
* mrai2: [interval] in seconds, it indicates the per link (i, j) minimum route ADV interval for node termination2.
* ip_eth_n1: [add/netmask] ip addr of the interface of termination1
* ip_eth_n2: [add/netmask] ip addr of the interface of termination2

###Graph example

Inside the file `graphExample` there is an example of graph with all the attributes needed to use the advanced options