#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns10
ip netns exec ns10 ip link set lo up

# create a port pair
ip link add tap10 type veth peer name br-tap10

# attach one side to linuxbridge
brctl addif br-iof br-tap10

# attach the other side to namespace
ip link set tap10 netns ns10

# set the ports to up
ip netns exec ns10 ip link set dev tap10 up
ip link set dev br-tap10 up

# Add ip addresses related to this AS
ip netns exec ns10 ip address add 10.0.0.54/30 dev tap10
ip netns exec ns10 ip address add 10.0.0.62/30 dev tap10
