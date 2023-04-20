#!/bin/bash
#
#SBATCH --job-name=map_abq
#SBATCH --output=%x.o%j
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=10gb
#SBATCH --time=100:00:00
#SBATCH --partition=debug
#SBATCH --nodelist=hengst
#
# To compute in the submission directory
cd /usrtmp/valmalette/abakubc_1404/src
#
python3 full_runner.py
