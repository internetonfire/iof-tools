#!/bin/bash

# This script can be used to count the number of cpus reserved
# After setting up the environment, copy it in the cpu_info dir and execute it.

tot=0

for f in `ls node*`
do
  cpu=`cat $f | json_pp | grep "ansible_processor_vcpus" | cut -d ":" -f2 | cut -d"," -f1 | cut -d " " -f2`
  tot=$((tot + cpu))  
done
echo $tot
