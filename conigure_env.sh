#!/usr/bin/env bash

apt-get install python python-m2crypto python-dateutil python-openssl libxmlsec1 xmlsec1 libxmlsec1-openssl libxmlsec1-dev autoconf python-pip python3-pip ansible default-jdk
pip3 install networkx==2.4rc1 jinja2
cd "$HOME" || exit
mkdir src
cd src || exit
git clone https://ans.disi.unitn.it/redmine/iof-tools.git
cd iof-tools || exit
git checkout reorganizedVersion
cd "$HOME"/src || exit
git clone https://github.com/GENI-NSF/geni-tools omni
cd omni || exit
./autogen.sh
./configure
make
cd "$HOME"/src/iof-tools || exit
ln -s "$HOME"/src/omni/src/omni omni
export PATH="$PATH:."
openssl rsa -in twist-encrypt.key -out twist.key
openssl x509 -pubkey -noout -in ~/.ssh/twist.cert > ~/.ssh/twist.pub

