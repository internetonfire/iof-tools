#!/usr/bin/env bash

apt-get install python python-m2crypto python-dateutil python-openssl libxmlsec1 xmlsec1 libxmlsec1-openssl libxmlsec1-dev autoconf python-pip python3-pip ansible default-jdk
pip3 install networkx==2.4rc1 jinja2
cd $HOME
mkdir src
cd src
git clone https://ans.disi.unitn.it/redmine/iof-tools.git
cd iof-tools
git checkout reorganizedVersion
cd $HOME/src
git clone https://github.com/GENI-NSF/geni-tools omni
cd omni
./autogen.sh
./configure
make
cd $HOME/src/iof-tools
ln -s $HOME/src/omni/src/omni omni
export PATH="$PATH:."
openssl rsa -in twist-encrypt.key -out twist.key
openssl x509 -pubkey -noout -in ~/.ssh/twist.cert > ~/.ssh/twist.pub

