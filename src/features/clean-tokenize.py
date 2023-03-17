'''
Script to clean and tokenize the texts from the parliamentary interventions. The following pre-processing is applied:

1. Removal of \n, \t, \r.
2. Removal of punctuation.
2. Removal of digits, spaces and words with two letters or fewer.
3. Removing a list of spanish stopwords.
4. Removing procedural words: señor/a, diputado/a, señoría, Presidente/a, Decreto, Ley, etc.
5. (Optional, based on argument 'lemmatised') Lemmatisation.
5. Tokenizing.

Usage: $python3 clean-tokenize.py [input file] [lemmatised (true/false)] [output file]

- input file: .csv file containing a dataframe with a column called «text» containing the documents to clean and tokenize.
- lemmatised: boolean argument. True = lemmatised tokens. False = not lemmatised.
- output file: the script returns a copy of the dataframe as .csv containing an additional column called «clean_text» with the list of tokens.
'''

import pandas as pd
import nltk
import gensim
import string
from nltk.tokenize import ToktokTokenizer
import spacy
import sys
import re

tok = ToktokTokenizer()

# Creating stopwords list.
procedural = ['muchas','diputado', 'diputada', 'diputados', 'diputadas', 'gobierno', 'gobiernos', 'oposición', 'exministro', 'ministro',
              'ministra', 'ministros', 'ministras', 'parlamento', 'parlamentario', 'congreso', 'pregunta', 'preguntar', 'ley',
              'leyes', 'decreto', 'decreto-ley', 'partido', 'partidos', 'grupo', 'señoras', 'señor', 'señora', 'señores', 'señoría',
              'señorías', 'voto', 'votar', 'decoro', 'cámara', 'presidente', 'presidenta', 'vicepresidente', 'vicepresidenta',
              'vicepresidentes', 'vicepresidentas', 'proposición', 'proposiciones', 'proyecto', 'no-ley', 'favor', 'gracias',
              'enmienda', 'enmiendas', 'moción', 'mociones', 'interpelación', 'interpelaciones', 'aplausos', 'usted', 'ustedes',
              'portavoz', 'portavoces', 'alusión', 'alusiones', 'comisión', 'comisiones', 'presupuesto', 'presupuestos', 'medida',
              'medidas', 'política', 'políticas', 'propuesta', 'propuestas', 'tribuna', 'pnl', 'regulación', 'herria', 'junts',
              'disposición', 'disposiciones', 'iniciativa']

# Mainly references to other parties or words in Galizan, Euskera or Català/Valencià, which are used by specific political parties.
other_stopwords = ['socialista', 'socialistas', 'popular', 'populares', 'ciudadanos', 'podemos', 'moitas', 'grazas', 'obrigado',
                   'egun', 'eskerrik', 'asko', 'moltes', 'gràcies', 'bon', 'día', 'buenos', 'días', 'ahora', 'además', 'aquí', 'allí',
                   'solo', 'sólo', 'sino', 'hoy', 'así', 'ejemplo', 'tan', 'senyor', 'senyora', 'toda', 'hecho', 'hacer', 'esquerra'
                   'bildu', 'pnv', 'psoe', 'pp', 'vox', 'hace', 'decir', 'dice', 'dijo', 'dicho', 'boas', 'tardes', 'bona', 'tarda',
                   'arratsalde', 'buenas', 'ciu', 'erc', 'iu', 'haber', 'convergència', 'pdecat', 'convergencia', 'verds', 'real', 'unió',
                   'confederal', 'comú', 'podem', 'marea', 'ciu', 'per']

stopwords = nltk.corpus.stopwords.words('spanish')

with open('spanish.txt') as f:
    words = f.readlines()

stopwords = stopwords + procedural + other_stopwords + words

def clean(text: str, lemmatise: bool = False) -> list:

    # Text to lowercase.
    text = text.lower()

    # Turning splitted words into 1, e.g. con-\ngreso to congreso.
    regex = r"([a-zA-ZñáéíóúüàèìòùçÑÁÉÍÓÚÜÀÈÌÒÙÇ])(\-\n)"
    text = re.sub(regex, '\1', text)

    # Removing \n, \t, \r.
    text = text.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')

    # Removing punctuation.
    text = text.translate(str.maketrans(
        string.punctuation, ' '*len(string.punctuation)))

    # Double spaces.
    text = text.replace('  ', ' ')

    # Removing en- and em-dashes, '«' and '»'.
    chars = ['-', '–', '-', '—', '«', '»', '―']
    for c in chars:
        text = text.replace(c, '')

    # Tokenizing.
    tokens = tok.tokenize(text)

    # Turning words that split in two into one. (e.g. ['presi-', 'dente'])
    for i in range(len(tokens)):
        if '\xad' in tokens[i]:
            tokens[i] = tokens[i].replace('\xad', '')
            if len(tokens) > i + 1:
                tokens[i] = tokens[i] + tokens[i+1]
                tokens[i+1] = ''

    tokens = [t for t in tokens if t != ''] 

    # Lemmatisation: first joining sentences and then lemmatising (the module 
    # splits it automatically).
    if lemmatise == True:

        ltz = spacy.load('es_core_news_sm')
        text = ' '.join(tokens)

        doc = ltz(text)
        lemmas = [ltz.lemma_ for ltz in doc]

        # Removing stop words, procedural words, short words and numbers.
        tokens = [w for w in lemmas if w not in stopwords and len(
            w) > 2 and w != ' ' and not w.isdigit()]

    else:
        tokens = [w for w in tokens if w not in stopwords and len(
            w) > 2 and w != ' ' and not w.isdigit()]

    return tokens

def main():
    assert len(sys.argv) == 4, 'Usage: python clean-tokenize.py [input file] [lemmatised (true/false)] [output file]'

    input_file = sys.argv[1]
    lemmatise = sys.argv[2]
    output_file = sys.argv[3]

    # Import data.
    dataframe = pd.read_csv(input_file)

    # Reduce data to only the rows with actual text.
    dataframe = dataframe.loc[dataframe['text'] != 0].dropna().reset_index(drop=True)
    dataframe = dataframe.loc[dataframe['text'] != "['nan']"].reset_index(drop=True)

    # Turn relevant column to list.
    corpus = dataframe['text'].to_list()

    # Clean the list. # TODO: is this causing the problem with lists as strings?
    clean_corpus = [clean((t), lemmatise) for t in corpus]

    # Create new column with clean tokens.
    print('Corpus cleaned.')
    dataframe['clean_text'] = clean_corpus

    # Create bigrams and trigrams.
    bigram = gensim.models.Phrases(dataframe['clean_text'], min_count=3, threshold=30)
    trigram = gensim.models.Phrases(bigram[dataframe['clean_text']], min_count=3, threshold=30)

    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)

    def get_phrases(x):
        return trigram_mod[bigram_mod[x]]

    dataframe['phrases'] = dataframe['clean_text'].loc[0:100].apply(get_phrases)
    print('Bigrams and Trigrams created.')

    # Re-sort by date.
    dataframe = dataframe.sort_values(by='fecha').reset_index(drop=True)

    # Save to output file.
    dataframe.to_csv(output_file, index=False)

    # Count total amount of tokens at the end.
    tot_count = 0
    for t in clean_corpus:
        tot_count += len(t)

    print(f'Succesfully cleaned and tokenized all texts ({tot_count} tokens). Results in {output_file}.')

main()
