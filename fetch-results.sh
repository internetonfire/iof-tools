#!/bin/bash
#
# Script to fetch experiment results from the testbed
#

usage () {
  echo "usage: $0 [ -d dir ]"
  echo "  options:"
  echo "    -d dir: directory containing the generated logs, if not specified the"
  echo "            'RESULTS' directory will be used"
  exit 1
}

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
  DIR="RESULTS"
fi

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Fetching results from the control node"
if [ -d $DIR ]
then
  echo "The output directory already exists, if you contiue all it's contents will be deleted."
  read -p "Delete the output dir? (y/n) " -n 1 -r
  echo ""
  if [[ $REPLY =~ ^[Yy]$ ]]
  then
    rm -r $DIR
  else
    exit 1
  fi
fi

scp -F ssh-config -r node0:$DIR . > /dev/null
if [ $? -ne 0 ]
then
  echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Error copying the files, exiting"
  exit 1
fi

# Extraction of the logfiles, the Directory structure is:
# OUTPUTDIR/runRUNNUMBER/[ tgz, logs ]
# eg. RESULTS/run3/tgz will contain the original compressed files
#     RESULTS/run3/logs will contain all the raw logs ready to be analyzed
#
echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Extracting the files"
cd $DIR
#ls
for d in `ls | grep run`
do
  cd $d
  for f in `ls *.tgz`
  do
    tar xzf $f
  done
  mkdir tgz
  mkdir logs
  #ls
  mv *.tgz tgz/
  mv node*-logs/* logs/
  rm -r node*-logs
  cd ..
done
cd ..

# Logs extracted, if this run is related to a Fabrikant topology we need to remove the logs related to the nodes used
# to generate the change in the network. These nodes are always the last three with highest ID.
echo "Extraction done. If this simulation is related to a Fabrikant topology, we need to remove the logs related to"
echo "the nodes used to generate the change in the network."
read -p "Is this simulation based on a Fabrikant topology? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then
  cd $DIR
  for d in `ls | grep run`
  do
    cd ${d}/logs
    # We have to remove the last three logfiles, but we must move the "RECONF" message from these nodes to the last
    # node on the gadget
    GADGETLAST=`ls | cut -d "_" -f3 | cut -d "." -f1 | sort -n | tail -4 | head -1`
    GADGETLOG="log_h_${GADGETLAST}.log"
    grep RECONF * | sed -E 's/^.*log://' >> $GADGETLOG
    for f in `ls | cut -d "_" -f3 | cut -d "." -f1 | sort -n | tail -3`
    do
      LOGREMOVAL="log_h_${f}.log"
      #echo "removing $LOGREMOVAL"
      rm $LOGREMOVAL > /dev/null
    done
    cd ../../
  done
  cd ..
fi

echo -n `date +"%Y-%m-%d %H:%M:%S"`; echo " Fetching and extraction done. You can now analyze and plot the logs."