#!/bin/bash
# 
# Simple script to check the Bird processes:
# This script checks (via birdc) all the BGP sessions of an AS.
# There must be an Established session for every "bgpSession_h*" config
# file present on the AS config dir. If not, the scripts throws an error.
#
# The scrpt takes two fixed parameters:
# 1) The directory of the config files of the AS to be checked
# 2) The path to the "birdc" binary

SESS_FILE=".birdsessions"

BIRD_CONF_PATH=$1
BIRDC_PATH=$2


cd $BIRD_CONF_PATH

$BIRDC_PATH/birdc -s $BIRD_CONF_PATH/sock* show protocols | grep BGP | awk '{ print $1 ";"$6 }' > $SESS_FILE 

for f in `ls $BIRD_CONF_PATH/bgpSession_h*`
do
  session_id=`echo $f | sed -e 's/^.*bgpSession_//' | sed -e 's/\.conf//'`
  state=`grep "$session_id;" $SESS_FILE | cut -d";" -f2`
  if [ "$state" != "Established" ]; then
    echo "Session $session_id error."
    exit 1
  fi
done
rm $SESS_FILE
echo "Ok."
