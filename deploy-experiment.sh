#!/bin/bash
#
# This script deploys all the experiment files needed on the Testbed
#
FORKS=25

usage () {
  echo "usage: $0 -d config dir"
  echo "  options:"
  echo "    -d dir: path of the directory generated with the BIRD Config generator"
  exit 1
}

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

#TODO - input getopt
while getopts ":d:" o; do
  case "${o}" in
    d)
      DIR=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done
shift $((OPTIND-1))

if [ -z "${DIR}" ]
then
  usage
fi

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Generating the deployment scripts"
cp check-sessions.sh $DIR
python3 gen-deploy.py -b $DIR
if [ $? -ne 0 ]
then
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Error generating the deployment scripts, exiting"
  exit 1
fi
echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Moving files on the control node"
scp -F ssh-config -r as.json nodi.json run-experiment.sh id.cert ansible.cfg ansible-hosts ssh-config-no-proxy playbooks/ node0: > /dev/null
if [ $? -ne 0 ]
then
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Error copying the files, exiting"
  exit 1
fi

ssh -F ssh-config node0 mv ssh-config-no-proxy ssh-config > /dev/null
if [ $? -ne 0 ]
then
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Error copying the files, exiting"
  exit 1
fi

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Deploying the experiment config on the testbed"
run_playbook deploy.yaml

echo "Ok, done. You can now connect to the control node with the command 'ssh -F ssh-config node0' and issue the command './run-experiment.sh' to start the simulation"