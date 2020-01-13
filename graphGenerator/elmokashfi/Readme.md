# AS graph generator

bgp.py contains the code of the generator I developed starting from [1].
It generates random NetworkX Graph objects following the algorithm published
in [1].

## Properties

Generated graphs have the following properties:
 1. They have a hierarchical structure, meaning there are not provider-customer 
	loops.
 2. The degree frequencies follow a power-law distribution.
 3. Degree-averaged clustering follow a power-law distribution.
 4. Average path length is around 4.

The file *test_main_properties.py* checks the aforementioned properties.
Besides properties 1,4, the properties 2,3 cannot be checked directly but they
are considered through plotting, as indicated in [1].

## Usage

While the interesting code is inside *bgp.py*, you can generate random AS graphs by calling:
```bash
	./generate.py <number_of_nodes> <number_of_graphs>
```
This will produce a series of graphml files in the current directory called *baseline-<number_of_nodes>-<id>.graphml*.

## Tests

Unit testing can be performed with:
```bash
	pytest -s test_internet_as_graph.py
```
Feature tests require the execution of
```bash
	./test_main_properties.py
```
and the analysis of the resulting images.

## References

[1] A. Elmokashfi, A. Kvalbein and C. Dovrolis, "On the Scalability of 
BGP: The Role of Topology Growth," in IEEE Journal on Selected Areas 
in Communications, vol. 28, no. 8, pp. 1250-1261, October 2010.
