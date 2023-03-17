
'''
This script trains a doc2vec model taking as argument a corpus with the structure
[{label}, {list of tokens}] as a .csv file. The model is trained creating vectors for each 
unique label. However, the corpus has repeating labels corresponding to the desired level 
of aggregation, e.g. a model for 1 legislature and using as labels the names of MPs, or 
a model for several legislatures using party-legislature as labels.

Usage: $python3 train-doc2vec.py [input file] [output file]

- input file: csv file with columns: [{label}, {list of tokens}].
- output file: path for the model to be saved.

'''

import gensim
import multiprocessing
import logging
import pandas as pd
import sys

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

cores = multiprocessing.cpu_count()
assert gensim.models.doc2vec.FAST_VERSION > -1

# Returns the corpus as a list of TaggedDocuments for the model to be able to read it.
def read_corpus(fname):
    for line in fname:
        yield gensim.models.doc2vec.TaggedDocument(line[1], [line[0]])

def train(train_corpus):

    # Declare model with the given hyperparameters.
    model = gensim.models.doc2vec.Doc2Vec(
        dm = 1,
        dm_mean = 1,
        dbow_words= 0,
        vector_size = 200,
        window = 10, # +- 10 words for the window size.
        min_count = 50, # Only include tokens that with a minimum count of 50 occurrences.
        workers = cores,
        epochs = 10,
        hs = 0,
        alpha = 0.025 # learning rate.
    )

    # Build the model vocabulary with the corpus.
    model.build_vocab(
        corpus_iterable= train_corpus
    )

    # Train the model.
    model.train(
        corpus_iterable = train_corpus, 
        total_examples = model.corpus_count,
        epochs = model.epochs
    )

    return model

def main():

    assert len(sys.argv) == 3, 'Usage: $python3 train-doc2vec.py [input file] [output file]'

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Read the .txt file as a list.
    corpus = pd.read_csv(input_file)
    corpus_as_list = corpus.values.tolist()

    # Turn into list of TaggedDocument.
    train_corpus = list(read_corpus(corpus_as_list))

    # Train the model.
    model = train(train_corpus)

    # Save the model.
    model.save(fname_or_handle = output_file)

main()
