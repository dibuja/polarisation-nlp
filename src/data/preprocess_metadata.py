'''
Script to pre_process the metadata of parliamentary interventions.

The script:

1. Concatenates all the legislatures files into 1 file with all metadata.
2. Removes irrelevant columns, keeping only legislature, date, initiative,
   initiative code, authors, name of session, speaker, pdf link.
3. Removes errors from legislature 3, 4, 6.
4. Turns date into datetime format.
5. Removes the page reference from the PDF links, since it is irrelevant and 
   slows the process down.
6. Removes duplicates and sort by date and pdf link.
7. Eliminates NaNs.
8. Replaces the roman numbers for legislature.

Usage: $python preprocess_metadata.py [directory with files] [output file]

'''

import pandas as pd
import os
import glob
import re


# Eliminate around 15 rows in L03 that are missplaced.
ERRORS_L3 = ['NUÑEZ ENCABO, MANUEL (GS)', 'MOYA PUEYO, VICENTE',
             'PEREZ RUBALCABA, ALFREDO', 'TOCINO BISCAROLASAGA, ISABEL (GCP)',
             'OLLERO TASSARA, ANDRES (APDP)',
             'MONTESINOS GARCIA, JUAN ANTONIO (GCP)',
             'CUENCA I VALERO, MARIA EUGENIA (GMC)',
             'GARCIA FONSECA, MANUEL (AIU-EC)', 'VILLAMOR LEON, JOSE']


# Eliminate 4 rows of data with errors.
ERRORS_L4 = ['COMPARECENCIA DE AUTORIDADES Y FUNCIONARIOS EN COMISION.',
             'COMPARECENCIA DEL GOBIERNO EN COMISION (ART. 44).']


def preprocess(dir: str) -> pd.DataFrame:
    os.chdir(f'./{dir}')

    # Get all the file names.
    filenames = [i for i in glob.glob('*.csv')]

    files = []
    for i in range(0, len(filenames)):
        files.append(pd.read_csv(filenames[i]))

    # Concatenate all files in one.
    data = pd.concat(files) 

    # Keep only useful fields.
    data = data[['legislatura', 'fecha', 'objeto_iniciativa',
                 'numero_expediente', 'autores', 'nombre_sesion',
                 'orador', 'enlace_pdf']]

    # Eliminate around 15 rows in L03 that are missplaced and others in L04.
    data = data.drop(data.loc[data['fecha'].isin(ERRORS_L3)].index)
    data = data.drop(data.loc[data['legislatura'].isin(ERRORS_L4)].index)

    # Eliminating 2 rows in L06 that are missplaced.
    data = data.loc[(data['fecha'] != 'Pregunta-Contestación')]

    # Date to datetime format.
    data['fecha'] = pd.to_datetime(data['fecha'], format='%d/%m/%Y')

    # Removing the  page reference since it is not needed and does not allow to
    # drop duplicates.
    data = data.astype({'enlace_pdf': 'string'})
    data['enlace_pdf'] = data['enlace_pdf'].str.replace(
        r'\#page=[\d]{1,3}', '')
    
    # Remove duplicates.
    data = data.sort_values(by=['fecha', 'enlace_pdf']
                            ).drop_duplicates().reset_index(drop=True)

    # Eliminate NaNs.
    data = data.dropna()

    # Eliminate rows if they correspond to constitution of commissions because 
    # these are irrelevant.
    data = data[data['objeto_iniciativa'].str.contains(
        'Constitución de la Comisión') == False].reset_index(drop=True)
    

    # Substitute roman numbers for integers values.
    data['legislatura'] = data['legislatura'].replace(
        {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 
        'VIII': 8, 'IX': 9, 'X': 10, 'XI': 11, 'XII': 12, 'XIII': 13, 
        'XIV': 14})

    return data

if __name__ == '__main__':

    assert len(
        sys.argv) == 3, 'Usage: python preprocess_metadata.py [directory with files] [output file]'

    dir = sys.argv[1]
    output_file = sys.argv[2]

    data = preprocess(dir)
    data.to_csv(f'../{output_file}', index=False)

    print('Finished pre-processing metadata.')
