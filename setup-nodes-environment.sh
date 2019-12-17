#!/bin/bash
#
# This script takes care of setting up the environment needed on the freshly booted testbed nodes

FORKS=25

run_playbook () {
# This function runs an ansible playbook, sometimes when using a lot of nodes the playbook
# could fail due to problems related to ansible timeouts. If the command fails we try to
# rerun it two times.
#
  PLAYBOOK=$1
  ansible-playbook --forks=$FORKS $PLAYBOOK > .ansib_out
  if [ $? -eq 0 ]
    then
      return
    else
      for i in {2..3}
      do
        echo "Playbook, failed trying to fix it, run $i"
        RETRYFILE=`grep "use: --limit" .ansib_out | cut -d"@" -f2`
        ansible-playbook --forks=$FORKS $PLAYBOOK --limit @$RETRYFILE
        if [ $? -eq 0 ]
        then
          return
        fi
      done
      echo "Something went wrong with this ansible playbook: $PLAYBOOK"
      echo "exiting."
      exit 1
    fi
}

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Setting up software on the nodes, this may take a while.."
run_playbook playbooks/setup-nodes.yaml

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Setting up syslog collector..."
run_playbook playbooks/setup-syslog.yaml

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Done. You can now use the './deploy-experiment.sh' script to deplon an experiment on the testbed"