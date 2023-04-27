#!/bin/bash
cd $1
if [ ! -z "$1" ]
  then
    abaqus_2021 job=$1 -memory "2000MB" -scratch "." interactive
fi

if [ ! -z "$2" ]
  then
    abaqus_2021 job=$2 -memory "2000MB" -scratch "." interactive
fi

if [ ! -z "$3" ]
  then
    abaqus_2021 job=$3 -memory "2000MB" -scratch "." interactive
fi
