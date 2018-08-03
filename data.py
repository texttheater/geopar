import json
import os
import random
import terms


def read_geoquery_file(path):
    result = []
    with open(path) as f:
        for line in f:
            term = terms.from_string(line)
            words = [str(w) for w in term.args[0].elements]
            mr = term.args[1]
            result.append((words, mr))
    return result


def read_oracle_file(path):
    result = []
    with open(path) as f:
        for line in f:
            line = json.loads(line)
            words = line['words']
            actions = [tuple(a) for a in line['actions']]
            result.append((words, actions))
    return result


def geo880_train():
    path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-train')
    return read_geoquery_file(path)

 
def geo880_test():
    path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-test')
    return read_geoquery_file(path)


def geo880_train_val():
    """Returns a random train-val split from the data.

    Includes 60 validation examples and 539 training oracles.
    """
    examples = geo880_train()
    oracles = read_oracle_file('oracles.json')
    combined = list(zip(examples, oracles))
    random.shuffle(combined)
    val_examples = [example for example, oracle in combined[:60]]
    train_oracles = [oracle for example, oracle in combined[60:]]
    return train_oracles, val_examples
