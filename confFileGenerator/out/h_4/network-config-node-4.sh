#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns4
ip netns exec ns4 ip link set lo up

# create a port pair
ip link add tap4 type veth peer name br-tap4

# attach one side to linuxbridge
brctl addif br-iof br-tap4

# attach the other side to namespace
ip link set tap4 netns ns4

# set the ports to up
ip netns exec ns4 ip link set dev tap4 up
ip link set dev br-tap4 up

# Add ip addresses related to this AS
ip netns exec ns4 ip address add 10.0.0.2/30 dev tap4
ip netns exec ns4 ip address add 10.0.0.13/30 dev tap4
ip netns exec ns4 ip address add 10.0.0.17/30 dev tap4
