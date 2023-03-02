'''
This script generates the corpus as a .csv file with the format [label, document].

The label is: '{political_group}-{legislature}'

Usage: $python3 generate-corpus.py [input file] [output file]

- input file: csv file with entire dataset.
- output file: path for the corpus to be saved.

'''

# TODO: Implement other ways of generating corpus, e.g. by PG-Year, PG-month, MP, MP-Year, MP-Legislature, etc.
# TODO? Implement a function to select time window.

import pandas as pd
import sys

def main():
    assert len(sys.argv) == 3, 'Usage: python3 generate-corpus.py [input file] [output file]'

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    df = pd.read_csv(input_file)

    # We create a new column called 'political_group_legis' concatenating the content of two columns.
    df['political_group_legislature'] = df['political_group'] + ' L' + df['legislatura'].astype(str)

    # Keep only relevant columns.
    df = df[['political_group_legislature', 'clean_text']]

    # Rename labels.
    df.columns = ['label', 'document']

    # Save to path.  
    df.to_csv(output_file, index=False)

main()