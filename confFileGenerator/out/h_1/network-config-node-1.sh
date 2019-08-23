#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns1
ip netns exec ns1 ip link set lo up

# create a port pair
ip link add tap1 type veth peer name br-tap1

# attach one side to linuxbridge
brctl addif br-iof br-tap1

# attach the other side to namespace
ip link set tap1 netns ns1

# set the ports to up
ip netns exec ns1 ip link set dev tap1 up
ip link set dev br-tap1 up

# Add ip addresses related to this AS
ip netns exec ns1 ip address add 10.0.0.14/30 dev tap1
