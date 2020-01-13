#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns7
ip netns exec ns7 ip link set lo up

# create a port pair
ip link add tap7 type veth peer name br-tap7

# attach one side to linuxbridge
brctl addif br-iof br-tap7

# attach the other side to namespace
ip link set tap7 netns ns7

# set the ports to up
ip netns exec ns7 ip link set dev tap7 up
ip link set dev br-tap7 up

# Add ip addresses related to this AS
ip netns exec ns7 ip address add 10.0.0.33/30 dev tap7
ip netns exec ns7 ip address add 10.0.0.37/30 dev tap7
