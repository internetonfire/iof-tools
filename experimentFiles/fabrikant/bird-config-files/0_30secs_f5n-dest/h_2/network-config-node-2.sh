#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns2
ip netns exec ns2 ip link set lo up

# create a port pair
ip link add tap2 type veth peer name br-tap2

# attach one side to linuxbridge
brctl addif br-iof br-tap2

# attach the other side to namespace
ip link set tap2 netns ns2

# set the ports to up
ip netns exec ns2 ip link set dev tap2 up
ip link set dev br-tap2 up

# Add ip addresses related to this AS
ip netns exec ns2 ip address add 10.0.0.6/30 dev tap2
ip netns exec ns2 ip address add 10.0.0.10/30 dev tap2
ip netns exec ns2 ip address add 10.0.0.13/30 dev tap2
ip netns exec ns2 ip address add 10.0.0.17/30 dev tap2
