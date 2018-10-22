import data
import lexicon
import parser
import pickle
import sys


if __name__ == '__main__':
    lex = lexicon.read_lexicon('lexicon.txt')
    with open('model.pickle', 'rb') as f:
        model = pickle.load(f)
    test_examples = data.geo880_test()
    total = 0
    parsed = 0
    correct = 0
    for words, gold_mr in test_examples:
        total += 1
        try:
            pred_mr = parser.parse(words, lex, model)
        except ValueError:
            print('no parse for', words, file=sys.stderr)
            continue
        parsed += 1
        if pred_mr.equivalent(gold_mr):
            correct += 1
    coverage = parsed / total
    recall = correct / total
    precision = correct / parsed
    print('coverage', coverage, 'recall', recall, 'precision', precision)


