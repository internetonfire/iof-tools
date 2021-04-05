#!/bin/bash
#
# Use this script to run from a single iof-log file to the corresponding path file

FILE="None"
OUTPUT="None"
NH=false

usage () {
		echo "Usage: $0 [OPTIONS]"
		echo "options:"
		echo "-f [value] 	log file to parse, MUST respect the 'log_n_x.log' format"
		echo "-o [value] 	output file to create"
		echo "-n 		Next hop flag, use it to include the 'from' field in the "
		echo "		output csv (default: false)"
		exit 0
}

file_exists(){
    if [ ! -f "$1" ]; then
        echo "$1 does not exist."
        exit 1
    fi
}

file_not_exists(){
		if [ -f "$1" ]; then
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
		    FILE=${OPTARG}
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

file_exists $FILE
file_not_exists $OUTPUT
asn_num=$(asn_number $FILE)

if $NH; then
		grep -oP "[0-9]*\.[0-9]*\.[0-9]*\.0.*NEW_BEST_PATH" ${FILE} | awk -F ',' -v asn=$asn_num -f single_file_nh.awk > ${OUTPUT}
else
		grep -oP "[0-9]*\.[0-9]*\.[0-9]*\.0.*NEW_BEST_PATH" ${FILE} | awk -F ',' -v asn=$asn_num -f single_file.awk > ${OUTPUT}
fi
