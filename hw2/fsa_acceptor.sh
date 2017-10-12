#!/bin/sh
fsa=$1
input=$2
while read line
do
  echo $line | carmel -sli $fsa 
done < $input



