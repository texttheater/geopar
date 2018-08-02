def ngrams(n, words):
    for i in range(len(words) - n + 1):
        yield tuple(words[i:i + n])


# https://stackoverflow.com/a/44661895/792749
# Subbag test for collection.Counter objects
def issubset(X, Y):
    return all(v <= Y[k] for k, v in X.items())


def startswith(a, b):
    if len(a) < len(b):
        return False
    return a[:len(b)] == b
