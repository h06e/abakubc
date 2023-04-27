#!/bin/bash
#SBATCH --job-name=abaqus
#SBATCH --output=%x.o%j
#SBATCH --error=%x.o%j
# Adapt number of MPI processes
#SBATCH --ntasks=2
# Adapt mem
#SBATCH --mem=5gb
# Adapt time
#SBATCH --time=00:20:00
## see doc for partition
#SBATCH --partition=cpu_short
##SBATCH --mail-type=END
##SBATCH --mail-user=firstname.lastname@centralesupelec.fr
cd ${SLURM_SUBMIT_DIR}
module load abaqus-mssmat/2021/gcc-9.2.0
alias abaqus_2021="abaqus"
python3 src/runner.py $SLURM_NTASKS campagne_test
