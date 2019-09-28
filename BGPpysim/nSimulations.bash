#!/usr/bin/env zsh

N=$1
DIRECTORY="out"

if [ ! -d "$DIRECTORY" ]; then
  mkdir "$DIRECTORY"
fi

for (( i = 0; i < $N; i++ )); do
    python3 bgpSimulator.py -g test.graphml
done