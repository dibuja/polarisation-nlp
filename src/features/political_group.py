'''
Creates a new feature called «political_group» that includes the political 
group of each speaker. Groups are merged to keep a constant label throughout 
the entire time period.

Usage: $python political_group.py [input file] [output file]'
'''

import pandas as pd
import re

group_merger = {
    # UP, IP, IU & Co.
    'GCUP-EC-GC': 'UP',
    'GCUP-EC-EM': 'UP',
    'GP-EC-EM': 'UP',
    'GIU': 'UP',
    'GIU-IU-ICV': 'UP',
    'GIP': 'UP',
    'GIU-ICV': 'UP',
    'IULV-CA': 'UP',

    # PP.
    'GP': 'PP',
    'PPC': 'PP',

    'GS': 'PSOE',   # PSOE.
    'GCs': 'CS',    # Ciudadanos.
    'GVOX': 'VOX',  # Vox.
    'GC-CiU': 'CIU',  # CIU.

    # PNV.
    'GV-PNV': 'PNV',
    'GV (EAJ-PNV)': 'PNV',

    # EH Bildu.
    'GEH Bildu': 'EHB',

    # ERC.
    'GER-IU-ICV': 'ERC',  # Since it was mostly ERC and almost no IU.
    'GR': 'ERC',
    'GER': 'ERC',
    'ERC': 'ERC',
    'GER-ERC': 'ERC'}

def political_group(data):

   # Adding the political group as a new feature.
    political_group = data['orador'].str.split(r' \(', 1)


    # Filling the cases where there is no political group.
    for i in range(len(political_group)):
        try: political_group[i][1]
        except: political_group[i].append('')


    # Clean the list to only include the political group, e.g. GP, GCUP-EC-GC.
    political_group = [political_group[i][1][:-1]
                       for i in range(len(political_group))]

    return political_group
    
if __name__ == '__main__':

    assert len(
        sys.argv) == 3, 'Usage: python political_group.py [input file] [output file]'

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    data = pd.read_csv(input_file)
    pgs = political_group(data)
    data['political_group'] = pgs

    data ['political_group'] = data['political_group'].replace(group_merger)

    data.to_csv(output_file, index=False)

    print('Finished pre-processing political groups.')
