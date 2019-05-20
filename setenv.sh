if [ $# -eq 1 ]; then
	testbed="$1"
else
	testbed="twist"
fi

if [ "$testbed" == "wilab" ]; then
	MASTER_NODE=nuc0-43
	CONFIG_FILE=$HOME/.ssh/wilab1-ssh.cfg
elif [ "$testbed" == "twist" ]; then
	MASTER_NODE=nuc4
	CONFIG_FILE=$HOME/.ssh/twist-ssh.cfg
else
	MASTER_NODE=proxy0
	CONFIG_FILE=./ssh-config
fi

HOME_FOLDER=`ssh -F ${CONFIG_FILE} ${MASTER_NODE} "pwd"`
