import os
import glob
import pandas as pd
import sys

assert len(sys.argv) == 3, 'Usage: python concatenate.py [relative path]'\
                        ' [output file] [delimiter]'

workdir = sys.argv[1] # e.g. 'by-legislature'
title = sys.argv[2] # e.g. 'all-interventions.csv'
delimiter = sys.argv[3] # e.g. ';'

os.chdir(f'./{workdir}')

# Get all the file names.
filenames = [i for i in glob.glob('*.csv')]

# Change all "; " for ", " to fix all the CSV files where \
# initative names include a semicolon.
for f in filenames:
    text = open(f"{f}", "r")
    text = ''.join([i for i in text]).replace("; ", ", ")
    x = open(f"{f}","w")
    x.writelines(text)
    x.close()

# Get all files as dataframes in pandas.
files = []
for i in range(0, len(filenames) - 1):
    # print(f'{i}')
    files.append(pd.read_csv(filenames[i], delimiter=delimiter))

# Combine all files.
concatenated = pd.concat(files)

# Export.
concatenated.to_csv(f"../{title}", index=False, encoding='utf-8-sig')