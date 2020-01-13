#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns18
ip netns exec ns18 ip link set lo up

# create a port pair
ip link add tap18 type veth peer name br-tap18

# attach one side to linuxbridge
brctl addif br-iof br-tap18

# attach the other side to namespace
ip link set tap18 netns ns18

# set the ports to up
ip netns exec ns18 ip link set dev tap18 up
ip link set dev br-tap18 up

# Add ip addresses related to this AS
ip netns exec ns18 ip address add 10.0.0.102/30 dev tap18
ip netns exec ns18 ip address add 10.0.0.110/30 dev tap18
