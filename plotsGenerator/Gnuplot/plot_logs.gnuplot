if (!exists("outfile")) outfile='out.pdf'
if (!exists("inputfile")) inputfile='logs.txt'
if (!exists("type")) type=1
if (!exists("timeRange")) timeRange="[s]"
if (!exists("yrng")) yrng=20
if (!exists("y2rng")) y2rng=1000
if (!exists("xmin")) xmin=0
if (!exists("xmax")) xmax=30

set datafile separator ','
set ylabel "Number of AS" offset 2,0,0
set y2label "# of updates" offset -2.2,0,0
set xlabel "Time from route change ".timeRange offset 0,0.7,0
set y2tics
set ytics nomirror
set key outside center top horizontal
set yrange [0:yrng]
set y2range [0.01:y2rng]
set y2tics ( "10^{-2}" 0.01, "10^{-1}" 0.1, "1" 1, "10^{1}" 1e1, "10^{2}" 1e2, "10^{3}" 1e3, "10^{4}" 1e4, "10^{5}" 1e5, "10^{6}" 1e6 )
set xrange [xmin:xmax]
set term pdfcairo enhanced dashed size 6,3.5 font "Helvetica,18"
set output outfile
set logscale y2 10
if (type > 0) {
    plot inputfile i 1 u 1:2 w lp t 'Conv. ASes',\
    '' i 1 u 1:4 w l lt 2 dashtype 2 notitle,\
    '' i 2 u 1:2 w lp t 'RX Updates' axes x1y2,\
    '' i 3 u 1:2 w l t 'total updates' axes x1y2
} else {
    plot inputfile i 1 u 1:2 w lp t 'Converged ASes',\
    '' i 1 u 1:4 w l lt 2 dashtype 2 notitle
}
