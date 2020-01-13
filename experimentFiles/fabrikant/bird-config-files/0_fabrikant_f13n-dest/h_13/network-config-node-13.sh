#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns13
ip netns exec ns13 ip link set lo up

# create a port pair
ip link add tap13 type veth peer name br-tap13

# attach one side to linuxbridge
brctl addif br-iof br-tap13

# attach the other side to namespace
ip link set tap13 netns ns13

# set the ports to up
ip netns exec ns13 ip link set dev tap13 up
ip link set dev br-tap13 up

# Add ip addresses related to this AS
ip netns exec ns13 ip address add 10.0.0.74/30 dev tap13
ip netns exec ns13 ip address add 10.0.0.82/30 dev tap13
