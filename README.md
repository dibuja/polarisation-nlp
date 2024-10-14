# Analysing Political Polarisation using Natural Language Processing

This work analyses the levels of political polarisation in the Spanish parliament for years 2000 until 2023 using text data obtained from parliamentary speeches. Specifically, it tackles both the affective and ideological aspects of political elite polarisation. For that purpose, a literature review was performed, identifying the current state-of-the-art in terms of polarisation analysis in Spain and internationally, and a dataset was harvested from the parliamentary records and pre-processed utilising several techniques.

The dataset was then processed in three different ways: (1) checking the occurrence of topics and propagation of terminology in the parliament to analyse the discourse of MPs, (2) analysing the levels of ideological polarisation by ideologically placing each political group of each legislature in a 2-dimensional matrix using a document embedding model and dimensionality reduction, observing their evolution and calculating an ideological polarisation index, and (3) evaluating the sentiment in the speech using a lexicon-based and a transformer-based sentiment classifiers.

Results show an underlying increasing trend in elite ideological polarisation throughout the last 7 legislatures and levels of elite affective polarisation at an all-time high for the time period analysed. The levels of ideological placement and polarisation obtained are comparable to those in available research.

This work resulted into a [Master Thesis](https://github.com/dibuja/polarisation-nlp/blob/main/MSc%20Thesis.pdf) and a research paper ([preprint](https://osf.io/preprints/socarxiv/ry4g2)).

## Research Questions

```
RQ1: Are politics more polarised nowadays, both ideologically and from an affective perspective?
RQ2: How do political groups contribute to polarisation?
RQ3: How did the ideological polarisation in the parliament evolve over the years?
RQ4: How do specific events affect the level of negativity in the debate?
```

For that purpose, we are:

- [x] Gathering all the relevant data from https://congreso.es using scrapers and PDF parsers;  
- [x] Make the dataset publicly available;    
- [x] Pre-processing it to remove any irrelevant elements;  
- [x] Analysing topic occurrence;  
- [x] Analysing ideological polarisation using document embeddings;  
- [x] Analysing affective polarisation using VADER & Transformers.
