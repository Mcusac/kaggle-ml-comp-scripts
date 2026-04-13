from .hashing import hashable

def score_sum(guesses, getter):
    guess_list = list(guesses.values())
    scores = {}

    for g in guess_list:
        h = hashable(g["solution"])
        x = scores[h] = scores.get(h, [[], g["solution"]])
        x[0].append(g)

    scores = [(getter(sc), o) for sc, o in scores.values()]
    scores = sorted(scores, key=(lambda x: x[0]), reverse=True)

    ordered_outputs = [x[-1] for x in scores]
    return ordered_outputs