#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns0
ip netns exec ns0 ip link set lo up

# create a port pair
ip link add tap0 type veth peer name br-tap0

# attach one side to linuxbridge
brctl addif br-iof br-tap0

# attach the other side to namespace
ip link set tap0 netns ns0

# set the ports to up
ip netns exec ns0 ip link set dev tap0 up
ip link set dev br-tap0 up

# Add ip addresses related to this AS
ip netns exec ns0 10.0.0.1/30 dev tap0
