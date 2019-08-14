#!/usr/bin/env bash

ansible nodes -m setup --tree cpu_info -a 'gather_subset=!all,!min,hardware filter=ansible_processor_*'
ansible nodes -m setup --tree nw_info -a 'gather_subset=!all,!min,network filter=ansible_default_ipv4'
ansible nodes -m setup --tree nw_if -a 'gather_subset=!all,!min,network filter=ansible_interfaces'
