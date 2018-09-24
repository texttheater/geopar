import numpy as np


DIMENSION = 1024


class LocalFeatureVector:

    """Represents a parse item (without history).

    Contains a fixed-size array with one element per feature template.
    Its values are preliminary hashes, without history and not taking into
    account actions.
    """

    def __init__(self, voc, num_templates):
        self.num_templates = num_templates
        self.voc = voc
        self.vec = np.zeros(num_templates, dtype='int32')
        self.template_ids = np.arange(num_templates, dtype='int32')
        self.counter = 0

    def add(self, v1, v2=None, v3=None, v4=None):
        if self.counter >= self.num_templates:
            raise RuntimeError('all templates already filled')
        v1 = self.voc.w2i(v1)
        v2 = self.voc.w2i(v2)
        v3 = self.voc.w2i(v3)
        v4 = self.voc.w2i(v4)
        hsh = 7
        hsh = 11 * v1 + hsh
        hsh = 11 * v2 + hsh
        hsh = 11 * v3 + hsh
        hsh = 11 * v4 + hsh
        self.vec[self.counter] = hsh
        self.counter += 1

    def with_action(self, v1, v2=None, v3=None, v4=None, v5=None):
        if self.counter < self.num_templates:
            raise RuntimeError('only {} of {} slots filled'.format(self.counter, self.num_templates))
        v1 = self.voc.w2i(v1)
        v2 = self.voc.w2i(v2)
        v3 = self.voc.w2i(v3)
        v4 = self.voc.w2i(v4)
        v5 = self.voc.w2i(v5)
        vec = 29 * self.vec + self.template_ids
        vec = 29 * vec + v1
        vec = 29 * vec + v2
        vec = 29 * vec + v3
        vec = 29 * vec + v4
        vec = 29 * vec + v5
        vec = vec % DIMENSION
        kernel = np.zeros(DIMENSION, dtype='float32')
        for i in range(self.num_templates):
            kernel[vec[i]] += 1
        return kernel


def zeros():
    return np.ndarray(DIMENSION, dtype='float32')
