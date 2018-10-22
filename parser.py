import models
import parseitems
import random
import sys
import time
import util


def parse(words, lex, model):
    agenda = [parseitems.initial(words)]
    while any(not i.finished for i in agenda):
        agenda = [s for i in agenda for s in i.successors(lex)]
        agenda.sort(key=lambda i: model.score(i.features()), reverse=True)
        beam = agenda[:min(10, len(agenda))]
        agenda = beam
    if not agenda:
        raise ValueError('no parse found')
    return agenda[0].stack[0].mr


def train(train_data, val_data, lex, max_epochs, initial_patience):
    train_data = list(train_data)
    model = models.Perceptron()
    best_accuracy = 0
    best_model = model
    patience = initial_patience
    for t in range(max_epochs):
        start_time = time.time()
        random.shuffle(train_data)
        train_one_epoch(train_data, lex, model)
        # Validate and see if the model got better:
        val_model = model.copy()
        val_model.average_weights()
        val_coverage, val_accuracy, val_precision = validate(val_data, lex, val_model)
        elapsed = time.time() - start_time
        if val_accuracy > best_accuracy:
            best_accuracy = val_accuracy
            best_model = val_model
            patience = initial_patience
        else:
            patience -= 1
        print('epoch', t, 'elapsed', elapsed, 'coverage', val_coverage,
              'recall', val_accuracy, 'precision', val_precision,
              'patience', patience, file=sys.stderr)
        if patience == 0:
            break
    return best_model


def train_one_epoch(train_data, lex, model):
    for words, gold_action_sequence in train_data:
        def is_correct(item):
            return all(g == i for g, i in
                       zip(gold_action_sequence, item.action_sequence()))
        agenda = [parseitems.initial(words)]
        while any(not i.finished for i in agenda):
            agenda = [s for i in agenda for s in i.successors(lex)]
            agenda.sort(key=lambda i: model.score(i.features()), reverse=True)
            beam = agenda[:min(10, len(agenda))]
            if not any(is_correct(i) for i in beam):
                break # early update
            agenda = beam
        highest_scoring_item = agenda[0]
        highest_scoring_correct_item = next(i for i in agenda if is_correct(i))
        if highest_scoring_item != highest_scoring_correct_item:
            model.update(highest_scoring_correct_item.features(),
                         highest_scoring_item.features())


def validate(val_data, lex, model):
    total = 0
    parsed = 0
    correct = 0
    for words, gold_mr in val_data:
        total += 1
        try:
            pred_mr = parse(words, lex, model)
        except ValueError:
            print('no parse for', words, file=sys.stderr)
            continue
        parsed += 1
        if pred_mr.equivalent(gold_mr):
            correct += 1
    coverage = parsed / total
    recall = correct / total
    precision = correct / parsed
    return coverage, recall, precision
