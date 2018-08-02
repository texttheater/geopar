import models
import parseitems
import random
import util


random.seed(1337) # for reproducibility


def print_agenda(agenda):
    for item in agenda:
        print(item)
    print()


def dbg(agenda, is_correct):
    for item in agenda:
        if is_correct(item):
            print(item.action_sequence())
            return
    raise ValueError('no correct item on agenda')


def parse(words, lex, model):
    agenda = [parseitems.initial(words)]
    #print_agenda(agenda)
    while any(not i.finished for i in agenda):
        agenda = [s for i in agenda for s in i.successors(lex)]
        agenda.sort(key=lambda i: model.score(i.features()), reverse=True)
        beam = agenda[:min(10, len(agenda))]
        agenda = beam
        #print_agenda(agenda)
    if not agenda:
        raise ValueError('no parse found')
    return agenda[0].stack[0].mr


def train(train_data, val_data, lex, epochs):
    train_data = list(train_data)
    model = models.Perceptron()
    for t in range(epochs):
        random.shuffle(train_data)
        for words, gold_action_sequence in train_data:
            #print(words)
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
                #print(highest_scoring_item)
                #print(highest_scoring_correct_item)
                #print()
                model.update(highest_scoring_correct_item.features(),
                             highest_scoring_item.features())
        validate(t, val_data, lex, model)
    model.average_weights()
    return model


def validate(epoch, val_data, lex, model):
    model = model.copy()
    model.average_weights()
    total = 0
    parsed = 0
    correct = 0
    for words, gold_mr in val_data:
        total += 1
        try:
            pred_mr = parse(words, lex, model)
        except ValueError:
            print('no parse for', words)
            continue
        parsed += 1
        if pred_mr.equivalent(gold_mr):
            correct += 1
    print('epoch', epoch, 'coverage', parsed / total, 'recall', correct / total, 'precision', correct / parsed)
