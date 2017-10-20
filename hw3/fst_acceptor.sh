#!/bin/sh

fsa=$1
input=$2
while read line
do
  output=$(echo "${line}" | carmel -kO 1 -sli ${fsa})
  if [ "$output" = "0" ]
  then
  echo "$line => *none* $output" 
  else
  echo "$line => $output"
  fi
done < $input

