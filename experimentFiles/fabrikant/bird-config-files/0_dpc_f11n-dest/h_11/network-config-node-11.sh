#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns11
ip netns exec ns11 ip link set lo up

# create a port pair
ip link add tap11 type veth peer name br-tap11

# attach one side to linuxbridge
brctl addif br-iof br-tap11

# attach the other side to namespace
ip link set tap11 netns ns11

# set the ports to up
ip netns exec ns11 ip link set dev tap11 up
ip link set dev br-tap11 up

# Add ip addresses related to this AS
ip netns exec ns11 ip address add 10.0.0.62/30 dev tap11
ip netns exec ns11 ip address add 10.0.0.70/30 dev tap11
