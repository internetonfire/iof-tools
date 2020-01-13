#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns12
ip netns exec ns12 ip link set lo up

# create a port pair
ip link add tap12 type veth peer name br-tap12

# attach one side to linuxbridge
brctl addif br-iof br-tap12

# attach the other side to namespace
ip link set tap12 netns ns12

# set the ports to up
ip netns exec ns12 ip link set dev tap12 up
ip link set dev br-tap12 up

# Add ip addresses related to this AS
ip netns exec ns12 ip address add 10.0.0.66/30 dev tap12
ip netns exec ns12 ip address add 10.0.0.74/30 dev tap12
