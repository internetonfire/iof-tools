#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns15
ip netns exec ns15 ip link set lo up

# create a port pair
ip link add tap15 type veth peer name br-tap15

# attach one side to linuxbridge
brctl addif br-iof br-tap15

# attach the other side to namespace
ip link set tap15 netns ns15

# set the ports to up
ip netns exec ns15 ip link set dev tap15 up
ip link set dev br-tap15 up

# Add ip addresses related to this AS
ip netns exec ns15 ip address add 10.0.0.81/30 dev tap15
ip netns exec ns15 ip address add 10.0.0.85/30 dev tap15
