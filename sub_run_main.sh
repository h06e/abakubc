#!/bin/bash
mkdir $1
cd $1
abaqus_2021 cae noGUI=../src/$2 -- $3 $4
