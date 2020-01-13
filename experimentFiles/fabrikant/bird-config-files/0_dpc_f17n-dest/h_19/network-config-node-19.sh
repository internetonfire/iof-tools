#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns19
ip netns exec ns19 ip link set lo up

# create a port pair
ip link add tap19 type veth peer name br-tap19

# attach one side to linuxbridge
brctl addif br-iof br-tap19

# attach the other side to namespace
ip link set tap19 netns ns19

# set the ports to up
ip netns exec ns19 ip link set dev tap19 up
ip link set dev br-tap19 up

# Add ip addresses related to this AS
ip netns exec ns19 ip address add 10.0.0.105/30 dev tap19
ip netns exec ns19 ip address add 10.0.0.109/30 dev tap19
