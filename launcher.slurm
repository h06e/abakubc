#!/bin/bash
#
#SBATCH --job-name=map_abq
#SBATCH --output=%x.o%j
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=30gb
#SBATCH --time=100:00:00
#SBATCH --partition=debug
#SBATCH --nodelist=hengst
#SBATCH --mail-user=robin.valmalette@ens-paris-saclay.fr
#SBATCH --mail-type=END
##cd
##code -r $SLURM_JOB_NAME.o$SLURM_JOB_ID
cd /usrtmp/valmalette/abakubc/
python3 src/runner.py $SLURM_NTASKS campagne_penrose
