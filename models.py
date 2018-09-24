import feature_vectors as fv
import numpy as np


class Perceptron:

    def __init__(self, update_counter=0, weights=(), totals=(), timestamps=()):
        self.update_counter = update_counter
        self.weights = np.zeros(fv.DIMENSION, dtype='float32')
        self.totals = np.zeros(fv.DIMENSION, dtype='float32')

    def score(self, features):
        return np.dot(features, self.weights)

    def update(self, correct_features, predicted_features):
        # TODO ???
        self.update_counter += 1
        update = correct_features - predicted_features
        self.weights += update
        self.totals += self.weights

    def average_weights(self):
        self.weights = self.totals / self.update_counter

    def copy(self):
        return Perceptron(self.update_counter, self.weights, self.totals)
