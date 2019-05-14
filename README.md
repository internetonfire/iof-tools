Internet on FIRE Scripts Repo
===

## ASSUMPTIONS

This `README` assumes that:
* you are working on a Unix-like system, so the variable `$HOME` is available;
* all the software will be in the `$HOME/src` folder;
* this repository has been cloned to `$HOME/src/iof-tools`;

Please execute the following beforehand:
```
mkdir -p $HOME/src
```

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
sudo apt install python-m2crypto python-dateutil python-openssl libxmlsec1 \
    xmlsec1 libxmlsec1-openssl libxmlsec1-dev autoconf
```

For other operating systems take a look at the official [wiki
page](https://github.com/GENI-NSF/geni-tools/wiki/QuickStart#debian--ubuntu)

### Omni installation

In order to install `omni` executes the following commands:

```
cd $HOME/src
git clone https://github.com/GENI-NSF/geni-tools omni
cd omni
./autogen.sh
./configure
make
cd $HOME/src/iof-tools
ln -s $HOME/src/omni/src/omni omni
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
