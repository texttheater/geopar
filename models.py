import collections


class Perceptron:

    def __init__(self, update_counter=0, weights=(), totals=(), timestamps=()):
        self.update_counter = update_counter
        self.weights = collections.Counter(weights)
        self.totals = collections.Counter(totals)
        self.timestamps = collections.defaultdict(int, timestamps)

    def score(self, features):
        result = 0.0
        for feature in features:
            result += self.weights.get(feature, 0.0)
        return result

    def update(self, correct_features, predicted_features):
        self.update_counter += 1
        update = collections.Counter()
        for cf in correct_features:
            update[cf] += 1
        for pf in predicted_features:
            update[pf] -= 1
        for feature, delta in update.items():
            if delta != 0:
                self.totals[feature] += (self.update_counter - self.timestamps[feature]) * self.weights[feature]
                self.timestamps[feature] = self.update_counter
                self.weights[feature] += delta

    def average_weights(self):
        for feature in self.weights:
            self.totals[feature] += (self.update_counter - self.timestamps[feature]) * self.weights[feature]
            self.timestamps[feature] = self.update_counter
            self.weights[feature] = self.totals[feature] / self.timestamps[feature]

    def copy(self):
        return Perceptron(self.update_counter, self.weights, self.totals, self.timestamps)
