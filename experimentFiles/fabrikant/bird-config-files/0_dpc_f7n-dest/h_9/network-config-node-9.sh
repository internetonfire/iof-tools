#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns9
ip netns exec ns9 ip link set lo up

# create a port pair
ip link add tap9 type veth peer name br-tap9

# attach one side to linuxbridge
brctl addif br-iof br-tap9

# attach the other side to namespace
ip link set tap9 netns ns9

# set the ports to up
ip netns exec ns9 ip link set dev tap9 up
ip link set dev br-tap9 up

# Add ip addresses related to this AS
ip netns exec ns9 ip address add 10.0.0.45/30 dev tap9
ip netns exec ns9 ip address add 10.0.0.49/30 dev tap9
