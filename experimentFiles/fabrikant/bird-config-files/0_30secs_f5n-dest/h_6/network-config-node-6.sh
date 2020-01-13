#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns6
ip netns exec ns6 ip link set lo up

# create a port pair
ip link add tap6 type veth peer name br-tap6

# attach one side to linuxbridge
brctl addif br-iof br-tap6

# attach the other side to namespace
ip link set tap6 netns ns6

# set the ports to up
ip netns exec ns6 ip link set dev tap6 up
ip link set dev br-tap6 up

# Add ip addresses related to this AS
ip netns exec ns6 ip address add 10.0.0.30/30 dev tap6
ip netns exec ns6 ip address add 10.0.0.38/30 dev tap6
