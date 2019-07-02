#Basic test

gen2 for now stable but it still uses `/30` networks for the point to point networks between nodes 

###Requirements

The generator require a well formed graph defined in graphml format generated with the function `internet_as_graph()` by the networkx library.

The function is not by default on the networkx library, you have to download and install it following this link:

`https://github.com/leonardomaccari/networkx/tree/bgp_topology`

Are also required the following python library:
* getopt
* os.path
* shutil
* sys
* ipaddress

###Test

launch the generator on a basic test

`python3 confFileGen.py --graph small_g.graphml --out out/`

If the file small_g.graphml is not founded it will be created with a predefined number of nodes (defined inside `constants.py`)

If the dir 'out/' does not exists it will be created

Now inside the folder `out` you will find all the files needed to start the nodes