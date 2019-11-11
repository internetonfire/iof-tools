# MRAI setter

This software takes in input a graphml annotated according to the specifications of IoF and set the node MRAI values.

## Usage

```
./mrai_setter.py <graphml_file> <strategy> <outputDir> <mean_mrai> [<advertising_node>]
```

The output dir will be created if it does not exist

The optional <advertising_node> option indicates *which node is advertising*.
This can be of paramount importance for some strategies (e.g., Fabrikant gadgets).

## Strategies

Strategies are MRAI setting policies.
At the time of writing available strategies include:
  * 30secs: set all timers to 30 seconds
  * none: set all timers to 0 seconds
  * fabrikant: set timers according to worst case gadget configuration (see paper)
  * inversefabrikant: inverted timers of the previous case (should lead to good case)
  * milanicent: set timers according to our theorecal derived model based on Milani centrality (mice)
  * milanicent2: variation of the previous one, with a different normalization factor
  * uniformdistrmrai: Set timers randomly following a uniform distribution btween 'default_mrai'%'percentage_constant' and default_mrai
  * constantfabrikant: Set timers following Fabrikant policies, but with a constant increment, the constant percentage is given by 'percentage_constant'
  * constantinversefabrikant: Set timers following inverse Fabrikant polices, but with a constant decrement, the constant percentage is given by 'percentage_constant'

## Tests

Just type
```
python3 -mpytest
```

