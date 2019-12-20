#!/bin/bash
#
# Script to run an experiment:
# INPUT: 
#  The first value is the AS Number of the process who will "break" the network
#  The second value is the filename of the bird broken adjacency session file
#
# Step 1: start bird processes
# Step 2: wait the network convergence

MAXMRAI=35

IOFLOG="/var/log/bird.log"
HOME=`pwd`
IOFPATH="$HOME/iof-bird-daemon"
NODESPATH="$IOFPATH/nodes-config"
FORKS=25

usage () {
  echo "usage: $0 -a AS [ -n Neighbor AS, -o dir, -r runs]"
  echo "  options:"
  echo "    -a AS: the 'Broken' Autonomous System number where the break occurs"
  echo "    -n Neighbor AS: The neighboring AS number where the break occurs. When the 'Broken' AS has more than"
  echo "                    a single adjacency session, this flag selects which specific session is going to"
  echo "                    be reconfigured. If not specifed, the first session will be selected."
  echo "    -o dir: output directory to save the generated logs, if not specified the"
  echo "            'RESULTS' directory will be used"
  echo "    -r runs: number of runs to execute for this experiment, if not specified"
  echo "             only one run will be executed"
  exit 1
}

wait_for_convergence () {
# This function waits for the experiment to converge, the idea is to check the bird log files
# of all our instances,if we don't see messages for a time bigger than the maximum MRAI in the
# network we can assume that no one is still sending updates and the network has reached convergence
#
  while (true)
  do 
    #LASTLOG=`tail -1 $IOFLOG | sed -E 's/(^.*)( bird.*)/\1/' | awk -F" " '{ print $1 " " $2 " " $3 }'`
    LASTLOG=`tail -1 $IOFLOG | awk -F" " '{ print $1 " " $2 " " $3 }'`
    LASTLOGSECONDS=`date -d "$LASTLOG" +%s`
    SECONDSNOW=`date +%s`
    ELAPSEDTIME=$(( SECONDSNOW - LASTLOGSECONDS ))
    echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Elapsed seconds since last change: $ELAPSEDTIME"
    if [ $ELAPSEDTIME -gt $MAXMRAI ]
    then
      echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " MAX MRAI ($MAXMRAI) timers expired, network has converged"
      return
    else
      sleep 10
    fi
  done
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

while getopts ":a:n:o:r:" o; do
  case "${o}" in
    a)
      AS=${OPTARG}
      ;;
    n)
      NEIGHBORAS=${OPTARG}
      ;;
    o)
      OUTDIR=${OPTARG}
      ;;
    r)
      RUNS=${OPTARG}
      ;;
    *)
      usage
      ;;
  esac
done
shift $((OPTIND-1))

if [ -z "${AS}" ]
then
  usage
fi
if [ -z "${OUTDIR}" ]
then
  OUTDIR="RESULTS"
fi
if [ -z "${RUNS}" ]
then
  RUNS=1
fi

if [ -d $OUTDIR ]
then
  echo "The output directory already exists, if you contiue all it's contents will be deleted."
  read -p "Delete the output dir? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    rm -r $OUTDIR
  else
    exit 1
  fi
fi
mkdir $OUTDIR

# TODO - FIX THIS with Ansible Deploy
sudo chmod 644 /var/log/bird.log

for (( i=1; i<=$RUNS; i++ )) 
do
  # First of all, let's start our simulation
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Starting the simulation number $i" 
  run_playbook playbooks/run-bird.yaml
  sleep 5
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Checking if everything started correctly" 
  run_playbook playbooks/check-birds.yaml

  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Simulation running, waiting for the network to converge"
  wait_for_convergence

  # Get the node where our bird daemon is running
  NODE=`grep -A1 "\"as\": $AS" as.json | tail -1 | sed -e 's/"//g' | cut -d ":" -f2 | cut -d " " -f2`
  #echo $NODE
  # The bird ID is the AS minus one
  BIRDID=$(( $AS - 1 ))

  COMPLETEPATH="$NODESPATH/h_$BIRDID"

  if [ -z "${NEIGHBORAS}" ]
  then
    FILEGOOD=`ssh -F ssh-config $NODE ls ${COMPLETEPATH}/bgpSession_h_* | grep conf | head -1 | sed -E 's/^.*bgp/bgp/'`
  else
    NEIGHBORID=$(( $NEIGHBORAS - 1 ))
    FILEGOOD="bgpSession_h_${BIRDID}_h_${NEIGHBORID}.conf"
  fi

  # Getting the good filename
  #FILEGOOD1=`echo $FILE | cut -d "-" -f1`
  #FILEGOOD="$FILEGOOD1.conf"

  echo $FILEGOOD
  echo $BIRDID



  # Backup of the good filename
  #ssh -F ssh-config $NODE cp $COMPLETEPATH/$FILEGOOD $NODESPATH/

  #if [ $? -ne 0 ]
  #then
	#  echo "err."
	#  exit 1
  #fi
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Breaking the link"
  #ssh -F ssh-config $NODE "cp $NODESPATH/$FILE $COMPLETEPATH/$FILEGOOD && $IOFPATH/birdc -s $NODESPATH/h_$BIRDID/sock$BIRDID configure"
  ssh -F ssh-config $NODE "sed -i -E 's/(^.*)(#)(bgp_path.prepend)/\1\3/' $COMPLETEPATH/$FILEGOOD && $IOFPATH/birdc -s $NODESPATH/h_$BIRDID/sock$BIRDID configure"
  if [ $? -ne 0 ]
  then
    echo "err."
    exit 1
  fi
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " The network has been reconfigured, waiting for convergence"
  wait_for_convergence

  ssh -F ssh-config $NODE "sed -i -E 's/(^.*)(bgp_path.prepend)/\1#\2/' $COMPLETEPATH/$FILEGOOD"
  #ssh -F ssh-config $NODE "cp $NODESPATH/$FILEGOOD $COMPLETEPATH/$FILEGOOD"
  
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Experiment done, fetching the logs"
  run_playbook playbooks/getlogs-bird.yaml
  #TODO mkdir precisa e spostamento logs
  mkdir $OUTDIR/run$i
  mv /tmp/node*.tgz $OUTDIR/run$i/
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Killing bird processes"
  run_playbook playbooks/kill-bird.yaml
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Run $i finished"
done

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Experiment finished, you can now go back on the virtual machine and fetch the logs, using the './fetch-results.sh' script"