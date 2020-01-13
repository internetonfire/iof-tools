#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns16
ip netns exec ns16 ip link set lo up

# create a port pair
ip link add tap16 type veth peer name br-tap16

# attach one side to linuxbridge
brctl addif br-iof br-tap16

# attach the other side to namespace
ip link set tap16 netns ns16

# set the ports to up
ip netns exec ns16 ip link set dev tap16 up
ip link set dev br-tap16 up

# Add ip addresses related to this AS
ip netns exec ns16 ip address add 10.0.0.90/30 dev tap16
ip netns exec ns16 ip address add 10.0.0.98/30 dev tap16
