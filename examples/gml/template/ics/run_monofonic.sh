#!/bin/bash
#SBATCH -J {{name}}_ics
#SBATCH -t 0-10:00:00
#SBATCH --mem 8G
#SBATCH --nodes 1
#SBATCH --ntasks-per-node 8
#SBATCH --cpus-per-task 1
#SBATCH --mail-type=all
#SBATCH --mail-user=ch4407@nyu.edu
#SBATCH --output=slurm-%x-%j.out
#SBATCH --error=slurm-%x-%j.out

echo
echo "Running on hosts: $SLURM_NODELIST"
echo "Running on $SLURM_NNODES nodes."
echo "Running on $SLURM_NPROCS processors."
echo "Current working directory is `pwd`"
echo

module purge
source /home/ch4407/env.sh
srun /home/ch4407/gml/codes/monofonic/build/monofonIC {{directory}}/ics/monofonic.conf

