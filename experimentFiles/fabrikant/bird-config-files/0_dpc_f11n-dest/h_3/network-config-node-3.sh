#!/bin/sh

# Namespace Configuration for this AS
ip netns add ns3
ip netns exec ns3 ip link set lo up

# create a port pair
ip link add tap3 type veth peer name br-tap3

# attach one side to linuxbridge
brctl addif br-iof br-tap3

# attach the other side to namespace
ip link set tap3 netns ns3

# set the ports to up
ip netns exec ns3 ip link set dev tap3 up
ip link set dev br-tap3 up

# Add ip addresses related to this AS
ip netns exec ns3 ip address add 10.0.0.14/30 dev tap3
ip netns exec ns3 ip address add 10.0.0.21/30 dev tap3
