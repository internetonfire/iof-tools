#!/usr/bin/env bash

ansible nodes -m setup --tree cpu_info -a 'gather_subset=!all,!min,hardware filter=ansible_processor_*'
