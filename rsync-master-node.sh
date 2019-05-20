#!/usr/bin/env bash

if [ $# -eq 1 ]; then
	testbed="$1"
else
	testbed="twist"
fi

. ./setenv.sh $testbed

IOF_FOLDER=${HOME_FOLDER}/iof-tools/

ssh -F ${CONFIG_FILE} ${MASTER_NODE} "mkdir -p ${IOF_FOLDER}"
rsync -avcz --exclude-from=rsync-ignore -e "ssh -F ${CONFIG_FILE} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" --progress ./ ${MASTER_NODE}:${IOF_FOLDER}
