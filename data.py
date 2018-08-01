import json
import os
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


def geo880_train_val(fold):
    oracle_path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-train-shuffled-oracles.json'.format(fold))
    val_path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-train-shuffled'.format(fold))
    oracles = read_oracle_file(oracle_path)
    val = read_geoquery_file(val_path)
    oracles = oracles[:fold * 60] + oracles[(fold + 1) * 60:]
    val = val[fold * 60:(fold + 1) * 60]
    return oracles, val
    
