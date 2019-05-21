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

In order to install `omni` execute the following commands:

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

### Omni configuration file

The `omni_config` file provided in this repository is a template of the `omni`
configuration file. Before running any other `omni` command, this template file
must be modified in order to adapt it to the local host environment.

First of all, we assume that the user running the omni commands has a
valid [iMinds Authority account](https://authority.ilabt.iminds.be/). We also
assume that the user's public and private keys associated with the iMinds
Authority account are located in ~/.ssh/twist.cert and ~/.ssh/twist.prk
respectively (the private key MUST NOT be encrypted
`openssl rsa -in ssl.key.secure -out ssl.key`).

The users whose public keys will be installed on the testbed's nodes are listed
(comma separated list) in the value of the `users` key in the `omni` section.
For each user listed in the `users` key, there is a corresponding section (named
after the user name) containing the specific configuration for that particular
user. For example, in the current template configuration file one of the user
is `segata`, and the corresponding configuration section looks like this:

```
[segata]
urn = urn:publicid:IDN+wall2.ilabt.iminds.be+user+segata
keys = ~/.ssh/twist.pub
```

The value of the field `keys` must be modified to point to the public key of the
user `segata`. The public key can be extracted from the certificate file with
```
openssl x509 -pubkey -noout -in ~/.ssh/twist.cert > ~/.ssh/twist.pub
```

In case you need to add a new user, these are the required steps:
1. append the new user name in the comma separated list of the `users` key in
   the `omni` section.
2. add to the `omni_config` file a new section for the new user.
3. commit and push the new `omni_config` template.

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
./gen-config.py -r <rspec file> -k <identity file>
```

The identity file is the private key or the certificate obtained after getting
an account from the [iMinds authority](https://authority.ilabt.iminds.be/).
This file will be copied under the current directory with the name `id.cert`.

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
