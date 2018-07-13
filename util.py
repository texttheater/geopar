def ngrams(n, words):
    for i in range(len(words) - n + 1):
        yield tuple(words[i:i + n])
