'''
This script reduces the dimension using either PCA or T-SNE by taking a model as an argument 
and returns a .csv file containing the 2 most relevant dimensions and the unique labels for 
each group of documents. Additionally, it creates an extra column with the colors of each 
party.

Usage: $python3 reduce-dimension.py [input file] [output file] [pca/tsne]

- input file: a gensim doc2vec model.
- output file: the path to save the .csv file.
- pca/tsne: method to reduce dimensionality.
'''

import gensim
import pandas as pd
import numpy as np
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

def reduce_dimension(model):
    
    labels = model.dv.index_to_key
    L = len(labels)
    M = model.vector_size

    z = np.zeros((L, M))

    for i in range(L):
        z[i,:] = model.dv[i]
    
    if method == 'tsne':
        dr = TSNE(n_components=2)
    elif method == 'pca':
        dr = PCA(n_components=2)
    else:
        raise ValueError('Methods allowed: "pca" or "tsne"')

    Z = dr.fit_transform(z)

    Z = pd.DataFrame(Z)
    z.columns = ['dim1', 'dim2']
    Z['label'] = labels

    return Z

def get_color(Z):
    labels = Z['label'].tolist()
    col = []

    for i in range(len(labels)):
        if '(GVOX)' in labels[i]:
            col.append('#82b431')
        elif '(GS)' in labels[i]:
            col.append('#c10200')
        elif '(GCs)' in labels[i]:
            col.append('#f87729')
        elif '(GP)' in labels[i]:
            col.append('#1eb3e6')
        elif '(GCUP-EC-GC)' in labels[i]:
            col.append('#a245b2')
        elif '(GR)' in labels[i]:
            col.append('#f99f00')
        elif '(GV (EAJ-PNV))' in labels[i]:
            col.append('#008146')
        elif '(GEH Bildu)' in labels[i]:
            col.append('#bbce00')
        else:
            col.append('#000000')

    Z['col'] = col
    return Z

def main():

    assert len(sys.argv) >= 3, 'Usage: python3 reduce-dimension.py [input file] [output file] [pca/tsne]'

    model_path = sys.argv[1]
    output_file = sys.argv[2]

    model = gensim.models.doc2vec.Doc2Vec.load(model_path)

    if sys.argv[3]:
        method = sys.argv[3]
    else:
        method = 'tsne'

    Z = reduce_dimension(model, method)
    Z = get_color(Z)

    Z.to_csv(output_file)

main()
