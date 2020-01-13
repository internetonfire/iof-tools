#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns5
ip netns exec ns5 ip link set lo up

# create a port pair
ip link add tap5 type veth peer name br-tap5

# attach one side to linuxbridge
brctl addif br-iof br-tap5

# attach the other side to namespace
ip link set tap5 netns ns5

# set the ports to up
ip netns exec ns5 ip link set dev tap5 up
ip link set dev br-tap5 up

# Add ip addresses related to this AS
ip netns exec ns5 ip address add 10.0.0.26/30 dev tap5
ip netns exec ns5 ip address add 10.0.0.33/30 dev tap5
