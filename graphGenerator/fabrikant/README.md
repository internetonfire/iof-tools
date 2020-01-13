## Fabrikant topology generator

You can use this generator to reproduce some topology presented in Fabrikant[1]

### Example of usage

`python3 gen_chain_gadget.py -i 1 -r 8 -t M -w fab17nodes.graphml`

This command will produce a graph with 17 nodes with 1 inner node per ring and 8 rings.
All the nodes will be of type M and the output is written into the file fab17nodes.graphml

You can also add the edge weight and set the MRAI directly on the graph, use the `--help` 
to have more info about the possible attributes.

### References

[1] A. Fabrikant, U. Syed, and J. Rexford, “There’s something about MRAI:
Timing diversity can exponentially worsen BGP convergence,” in 30th
IEEE Int. Conf. on Computer Communications (INFOCOM 2011),
Shanghai, China, Apr. 2011