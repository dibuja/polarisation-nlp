#!/bin/sh

# Job to run the code in an HPC Cluster @DTU.

#BSUB -J obt-txt
#BSUB -n 4
#BSUB -R "span[hosts=1]"
#BSUB -R "rusage[mem=6GB]"
#BSUB -W 4:00
#BSUB -u daniel.ansia@gmail.com
#BSUB -B
#BSUB -N

#BSUB -o output_%J.out
#BSUB -e errors_%J.err

module load python3
module load pandas/1.4.1-python-3.9.11

# Download code.
git clone https://github.com/dibuja/msc-thesis.git

# Move to the directory.
cd msc-thesis

# Install the requirements from the repository.
pip install -r requirements.txt

# Unzip data in the parent directory.
unzip data/vi-xiv-clean.csv.zip

# Create temporary directory.
mkdir tmp/
touch tmp/temp.pdf

# Obtain the texts taking the unzipped data and produce the outcome in out.csv.
python3 obtain-texts.py vi-xiv-clean.csv out.csv