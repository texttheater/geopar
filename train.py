#!/usr/bin/env python3


"""Train a semantic parsing model on the Geo880 data.
"""


import data
import lexicon
import parser
import pickle
import random


random.seed(1336) # for reproducibility


if __name__ == '__main__':
    lex = lexicon.read_lexicon('lexicon.txt')
    train_oracles, val_examples = data.geo880_train_val()
    model = parser.train(train_oracles, val_examples, lex, max_epochs=20, patience=3)
    with open('model.pickle', 'wb') as f:
        pickle.dump(model, f)
