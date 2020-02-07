
path="/home/leonardo/progetti/2019/Fed4Fire/data/RES-12K/"

tsfiles=($path/*30SEC*BROKEN*logs.txt)
fsfiles=($path/*15SEC*BROKEN*logs.txt)
DPCfiles=($path/*DPC*BROKEN*logs.txt)

echo $DPCfiles
for i in "${!DPCfiles[@]}"; do 
  gnuplot -e "inputfile30s='${tsfiles[$i]}'" -e "inputfile15s='${fsfiles[$i]}'" -e "inputfileDPC='${DPCfiles[$i]}'" -e "outputfile='${DPCfiles[$i]}.eps'" plots_by_distance_compared.gnuplot
done

return
for f in `ls $path/*BROKEN*_logs.txt`
    do echo $f;
    gnuplot -e "inputfile='$f'" plots_by_distance.gnuplot
done
