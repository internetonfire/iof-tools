#!/bin/bash
#
# Use this script to run from a single iof-log file to the corresponding path file

FOLDER="None"
OUTPUT="None"
NH=false

usage () {
		echo "Usage: $0 [OPTIONS]"
		echo "options:"
		echo "-f [value] 	log folder to parse, every file MUST respect "
		echo "		the 'log_n_x.log' format"
		echo "-o [value] 	output folder to use"
		echo "-n 		Next hop flag, use it to include the 'from' field in the "
		echo "		output csv (default: false)"
		exit 0
}

folder_exists(){
    if [ ! -d "$1" ]; then
        echo "$1 does not exist."
        exit 1
    fi
}

folder_not_exists(){
		if [ -d "$1" ]; then
				echo "$1 already exists."
				exit 1
		fi
}

asn_number(){
		file_name=$(basename "$1")
		log_num=$(cut -d "_" -f3 <<< ${file_name})
		asn_num=$(cut -d "." -f1 <<< ${log_num})
		echo $asn_num
}

while getopts ":f:o:n" o; do
    case "${o}" in
        f)
		    FOLDER=${OPTARG}
            ;;
		o)
		    OUTPUT=${OPTARG}
			;;
        n)
            NH=true
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

folder_exists $FOLDER
folder_exists $OUTPUT

num_files=$(ls -la $FOLDER | grep -o "\.log" | wc -l)
i=1
for file in "${FOLDER}/"*.log; do
		asn=$(asn_number $file)
		path_file="${OUTPUT}/node_${asn}.path"
		if $NH; then
				./single_file_handler.sh -f $file -o $path_file -n
		else
				./single_file_handler.sh -f $file -o $path_file
		fi
		echo -n "${i}/${num_files}" $'\r'
		i=$(($i + 1))
done
