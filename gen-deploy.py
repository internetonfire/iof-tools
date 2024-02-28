#!/usr/bin/env python
#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================

# This script manages the setup of the deployment files on the Testbed. Given the
# cpu resources reserved, and the Bird configuration directory, it will decide how
# to spread the AS on the physical nodes.

from argparse import ArgumentParser
from glob import glob
import json
import os
from random import randint

DEPLOY_TEMPLATE = "templates/ansible-deploy.template"

LOW_LATENCY = 2
HIGH_LATENCY = 13

# TODO: ask for a "savedirectory" on input and place everything there
DEPLOY_OUTFILE = "deploy.yaml"
ASLIST_OUTFILE = "as.json"
NODELIST_OUTFILE = "nodi.json"

def getASDistributionbyCpu(num_as,node_files):
    """
    This function distributes the AS nodes on the physical resources available.
    The distribution is done by cpu, trying to put an equal number of Bird processes on every core available.
    :param num_as: Number of Autonomous Systems to place
    :param node_files: Directory with info on nodes gathered by Ansible
    :return: node_list: List of Node objects [ { 'name': nodeX, 'cpus': total_cpus, 'as_list': [ list of ASes running on this node ]  } ]
    :return: as_list: List of ASes and their relative node [ { 'as': asnumber, 'node': nodeX } ]
    """
    node_list = []
    num_cpus = 0
    for n in node_files:
        with open(n) as nfd:
            dati = json.load(nfd)
            obj = {}
            obj['name'] = n.split("/", 1)[1]
            obj['cpus'] = dati['ansible_facts']['ansible_processor_vcpus']
            obj['as_list'] = []
            node_list.append(obj)
            num_cpus += obj['cpus']

    as_per_cpu = num_as / num_cpus
    as_list = []
    if as_per_cpu < 1:
        as_per_cpu = 1
    print(num_cpus)
    print(as_per_cpu)
    # Deploy an even number of ases on the nodes
    as_to_deploy = 1
    for n in node_list:
        for i in range(0,n['cpus']):
            for j in range(0,int(as_per_cpu)):
                if as_to_deploy <= num_as:
                    n['as_list'].append(as_to_deploy)
                    as_list.append({'as':as_to_deploy, 'node':n['name']})
                    as_to_deploy += 1

    # Now the nodes are evenly loaded, if we still have something to place, just put it
    # one per core
    if as_to_deploy < num_as:
        for n in node_list:
            for i in range(0,n['cpus']):
                if as_to_deploy <= num_as:
                    n['as_list'].append(as_to_deploy)
                    as_list.append({'as':as_to_deploy, 'node':n['name']})
                    as_to_deploy += 1

    return(node_list,as_list)

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-b","--birdconf",dest="birdconf",
                        default="",action="store",
                        help="Directory containing the bird config files, generated with the --directories flag")
    parser.add_argument("-n","--nodeconf",dest="nodeconf",
                        default="cpu_info",action="store",
                        help="Directory containing the output of the ansible cpu inventory for the nodes")

    args = parser.parse_args()
    bird_conf_dir = args.birdconf


    node_files = glob(args.nodeconf + "/node*")
    bird_files = glob(args.birdconf + "/h_*")

    if bird_conf_dir[-1] != '/':
        bird_conf_dir += '/'

    num_as = len(bird_files)
    #print(num_as)

    node_list, as_list = getASDistributionbyCpu(num_as,node_files)
    print(node_list)
    #print(as_list)

    # Given the AS to physical node assignment, we can now generate the deployment scripts.
    #
    # Wrap up scripts: we generate two scripts for every node, one to setup the network and
    # one to execute the bird daemons. Doing this one by one via ansible is too slow
    # The scripts are saved in the bird configuration directory
    for n in node_list:
        node_file_path = bird_conf_dir + n['name'] + ".sh"
        node_run_file_path = bird_conf_dir + n['name'] + "-run.sh"
        node_get_logs_path = bird_conf_dir + n['name'] + "-getlogs.sh"
        node_check_birds_path = bird_conf_dir + n['name'] + "-checkbirds.sh"

        node_script = "#!/bin/sh\n\n"
        run_script = node_script
        checkbirds_script = node_script
        node_get_logs = node_script

        node_get_logs += "mkdir $1/%s-logs\n" % (n['name'])

        for a in n['as_list']:
            node_id = a - 1
            cmd = "sh h_%d/network-config-node-%d.sh\n" % (node_id,node_id)
            node_script += cmd
            latencycmd = "tc qdisc add dev br-tap%d root netem delay %dms\n" % (node_id,randint(LOW_LATENCY,HIGH_LATENCY))
            node_script += latencycmd
            run_cmd = "cd $1/h_%d" % (node_id)
            run_cmd += " && truncate -s 0 log_h_%d.log && sudo ip netns exec ns%d ../../bird -c bgp_h_%d.conf -s sock%d\n" % (node_id,node_id,node_id,node_id)
            run_script += run_cmd
            run_script += "sleep 0.5\n"
            #run_script += "nohup ../bird_parse_routes.py -b ../../ -n sock%d > path_%d.log &\n" % (node_id,node_id)
            getlogs_cmd = "mv $1/h_%d/log_h_%d.log $1/%s-logs/ && touch $1/h_%d/log_h_%d.log\n" % (node_id,node_id,n['name'],
                                                                                                      node_id,node_id)
            getlogs_cmd += "mv $1/h_%d/path_%d.log $1/%s-logs/\n" % (node_id,node_id,n['name'])

            node_get_logs += getlogs_cmd
            checkbirds_script += "cd $1\n"
            checkbirds_script += "sh check-sessions.sh $1/h_%d $2\n" % (node_id)
            checkbirds_script += "if [ $? -ne 0 ]; then exit 1 ; fi\n"


        node_get_logs += "cd $1\n"
        node_get_logs += "tar -cz %s-logs -f $1/%s-logs.tgz\n" % (n['name'],n['name'])
        node_get_logs += "rm -rf $1/%s-logs\n" % (n['name'])

        with open(node_file_path,"w") as nw_fd:
            nw_fd.write(node_script)
        with open(node_run_file_path,"w") as nr_fd:
            nr_fd.write(run_script)
        with open(node_get_logs_path,"w") as nl_fd:
            nl_fd.write(node_get_logs)
        with open(node_check_birds_path,"w") as b_fd:
            b_fd.write(checkbirds_script)

    # Copying all the files is too slow, so we pack up all the config directory
    tar_file_name = bird_conf_dir[:-1] + ".tgz"
    tar_cmd = "tar -czf " + tar_file_name + " -C " + bird_conf_dir + " ."
    t = os.system(tar_cmd)
    if t != 0:
        print("Tarfile creation error.")
        exit(1)

    # We can now render our deploy template
    with open(DEPLOY_TEMPLATE, "r") as tpl_fd:
        deploy_tpl = tpl_fd.read()

    deploy = deploy_tpl % (tar_file_name)

    with open(DEPLOY_OUTFILE, "w") as dep_fd:
        dep_fd.write(deploy)

    with open(ASLIST_OUTFILE, "w") as as_fd:
        as_fd.write(json.dumps(as_list, indent=2, sort_keys=True))

    with open(NODELIST_OUTFILE, "w") as nodi_fd:
        nodi_fd.write(json.dumps(node_list, indent=2, sort_keys=True))
