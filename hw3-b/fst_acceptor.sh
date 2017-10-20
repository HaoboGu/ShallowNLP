#!/bin/sh

fsa=$1
input=$2
while read line
do
  output=$(echo "${line}" | carmel -k 1 -sli ${fsa})
  if [ "$output" = "" ]
  then
  echo "$line => no" 
  else
  echo "$line => yes"
  fi
done < $input

