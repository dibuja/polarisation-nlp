'''
Script to clean and tokenize the texts from the parliamentary interventions. The following pre-processing is applied:

1. Removal of \n, \t, \r.
2. Removal of punctuation.
2. Removal of digits, spaces and words with two letters or fewer.
3. Removing a list of spanish stopwords.
4. Removing procedural words: señor/a, diputado/a, señoría, President/a, Decreto, Ley, etc.
5. Tokenizing.

Usage: $python3 clean-tokenize.py [input file] [output file]

- input file: pandas dataframe with a column called «text» containing the documents to clean and tokenize.
- output file: the script returns a copy of the dataframe containing an additional column called «clean_text» with the list of tokens.
'''

import pandas as pd
import nltk
from gensim.utils import tokenize
import string
from nltk.tokenize import ToktokTokenizer
import spacy
import sys

tok = ToktokTokenizer()

# TODO: Evaluate if adding to the stowprds list: españa, españoles, españolas, presupuesto, presupuestos, medida, medidas, política, etc.
# TODO: Evaluate if adding to the stopwords list the basque, galizan and catalan words that would give away specific political parties.
# TODO: Evaluate if adding to the stopwords list the name of the political parties themselves: populares, popular, socialista, ciudadanos, podemos, etc.

procedural = ['diputado', 'diputada', 'diputados', 'diputadas', 'gobierno', 'gobiernos', 'oposición', 'exministro', 'ministro', 
              'ministra', 'ministros', 'ministras', 'parlamento', 'parlamentario', 'congreso', 'pregunta', 'preguntar', 'ley', 
              'leyes', 'decreto', 'decreto-ley', 'partido', 'partidos', 'grupo', 'señoras', 'señor', 'señora', 'señores', 'señoría', 
              'señorías', 'voto', 'votar', 'decoro', 'cámara', 'presidente', 'presidenta', 'vicepresidente', 'vicepresidenta', 
              'vicepresidentes', 'vicepresidentas', 'proposición', 'proposiciones', 'proyecto', 'no-ley', 'favor', 'gracias', 
              'enmienda', 'enmiendas', 'moción', 'mociones', 'interpelación', 'interpelaciones', 'aplausos', 'usted', 'ustedes',
              'portavoz', 'portavoces', 'alusión', 'alusiones', 'comisión', 'comisiones']

other_stopwords = ['ahora', 'además', 'aquí', 'allí', 'solo', 'sólo', 'sino', 'hoy', 'así', 'ejemplo']

def clean(text: list) -> list:
    # Removing \n, \t, \r.
    text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')

    # Text to lowercase.
    text = text.lower()

    # Removing punctuation.
    text = text.translate(str.maketrans(
        string.punctuation, ' '*len(string.punctuation)))

    # Double spaces.
    text = text.replace('  ', ' ')

    # Lemmatization.
    # TODO: Is lemmatization needed or even good?
    #proc = spacy.load('es_core_news_sm')
    #doc = proc(text)
    #lemmatized = [proc.lemma_ for proc in doc]

    # Tokenizing.
    tokens = tok.tokenize(text)

    # Stopwords + procedural words from the Spanish Parliament.
    stopwords = nltk.corpus.stopwords.words('spanish') + procedural + other_stopwords

    # Removing stop words, procedural words, short words and numbers.
    tokens = [w for w in tokens if w not in stopwords and len(w) > 2 and w != ' ' and not w.isdigit()]

    return tokens

def main():
    assert len(sys.argv) == 3, 'Usage: python clean-tokenize.py [input file] [output file]'

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Import data.
    dataframe = pd.read_csv(input_file)

    # Turn relevant column to list.
    corpus = dataframe['text'].to_list()

    # Clean the list.
    clean_corpus = [clean(str(t)) for t in corpus]

    # Create new column with clean tokens.
    dataframe['clean_text'] = clean_corpus

    # Save to output file.
    dataframe.to_csv(output_file, index=False)

    print(f'Succesfully cleaned and tokenized all texts. Results in {output_file}.')

main()