#!/usr/bin/env bash

sudo apt-get update
sudo apt-get -y install python python-m2crypto python-dateutil python-openssl libxmlsec1 xmlsec1 libxmlsec1-openssl libxmlsec1-dev autoconf python-pip python3-pip ansible default-jdk gnuplot-nox
pip3 install networkx==2.4rc1 jinja2 numpy pandas
cd "$HOME"/src || exit
git clone https://github.com/GENI-NSF/geni-tools omni
cd omni || exit
./autogen.sh
./configure
make
sudo make install
cd "$HOME"/src/iof-tools || exit
