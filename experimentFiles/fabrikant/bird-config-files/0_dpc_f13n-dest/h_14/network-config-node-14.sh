#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns14
ip netns exec ns14 ip link set lo up

# create a port pair
ip link add tap14 type veth peer name br-tap14

# attach one side to linuxbridge
brctl addif br-iof br-tap14

# attach the other side to namespace
ip link set tap14 netns ns14

# set the ports to up
ip netns exec ns14 ip link set dev tap14 up
ip link set dev br-tap14 up

# Add ip addresses related to this AS
ip netns exec ns14 ip address add 10.0.0.78/30 dev tap14
ip netns exec ns14 ip address add 10.0.0.86/30 dev tap14
