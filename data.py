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


def geo880_train():
    path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-train')
    return read_geoquery_file(path)

 
def geo880_test():
    path = os.path.join(os.path.dirname(__file__), 'data', 'geo880-test')
    return read_geoquery_file(path)
