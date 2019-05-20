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

## RSPEC generation

RSPEC files (extension .rspec) are XML files that describes which nodes to
allocate in a given testbed. For the TWIST and w.iLab1 testbeds the .rspec files
can be generated automatically using the `gen-rspec.py` script. The script
supports the following command line parameters:

* `-t` (`--testbed`): specifies which testbed the RSPEC will be generated for.
  Use twist for the TWIST testbed and wilab for w.iLab1;

* `-f` (`--filter`): comma separated list of node name prefixes. Only the
  available nodes whose name starts with one of the specified prefixes are
  inserted in the generated RSPEC. By default all the available nodes are used for
  generating the RSPEC file.

* `-n` (`--nodes`): comma separated list of node names. Only the available nodes
  whose name is listed with the `-n` option are inserted in the RSPEC file. By
  default all the available nodes are used. The `-n` option takes precedence over
  `-f`.

* `-w` (`--hardware`): comma separated list of hardware types (e.g., `pcgen05`)

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

## Generating SSH and Ansible config

After generating the `rspec` file, the `gen-config.py` script can generate
the SSH and the ansible configuration files to access the nodes of the
testbeds. To do so, simply run:

```
./gen-config.py -r <rspec file> -k <identity file>
```

The identity file is the private key or the certificate obtained after getting
an account from the [iMinds authority](https://authority.ilabt.iminds.be/).

This will generate:
* `ssh-config`: the configuration file to be given to the SSH command (e.g.,
  `ssh -F ssh-config ...`). This defines the names of the hosts as `node<i>`,
  for `i` going from 0 to N-1. To connect to one host, you can thus run
  `ssh -F ssh-config node0`.
* `ansible.cfg`: the Ansible configuration file.
* `ansible-hosts`: the Ansible inventory (list of nodes). In this file the
  group of nodes reserved for the experiments is named `nodes`. To test that
  this is properly working, try with `ansible nodes -m shell -a "uptime"`.

The filename of the configuration files can be changed via command line
arguments (see `./gen-config.py --help`).
