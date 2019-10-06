#!/usr/bin/env zsh

N=$1

./nSimulations.bash $N 30secs_test.graphml out30sec
./nSimulations.bash $N fabrikant_test.graphml outFabrikant
./nSimulations.bash $N inversefabrikant_test.graphml outInversefabrikant
./nSimulations.bash $N simpleheuristic_test.graphml outSimpleheuristic
./nSimulations.bash $N noMRAI_test.graphml outNoMRAI