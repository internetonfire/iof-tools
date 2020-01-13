#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns17
ip netns exec ns17 ip link set lo up

# create a port pair
ip link add tap17 type veth peer name br-tap17

# attach one side to linuxbridge
brctl addif br-iof br-tap17

# attach the other side to namespace
ip link set tap17 netns ns17

# set the ports to up
ip netns exec ns17 ip link set dev tap17 up
ip link set dev br-tap17 up

# Add ip addresses related to this AS
ip netns exec ns17 ip address add 10.0.0.98/30 dev tap17
ip netns exec ns17 ip address add 10.0.0.106/30 dev tap17
