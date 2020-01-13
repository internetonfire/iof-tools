#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns8
ip netns exec ns8 ip link set lo up

# create a port pair
ip link add tap8 type veth peer name br-tap8

# attach one side to linuxbridge
brctl addif br-iof br-tap8

# attach the other side to namespace
ip link set tap8 netns ns8

# set the ports to up
ip netns exec ns8 ip link set dev tap8 up
ip link set dev br-tap8 up

# Add ip addresses related to this AS
ip netns exec ns8 ip address add 10.0.0.42/30 dev tap8
ip netns exec ns8 ip address add 10.0.0.50/30 dev tap8
