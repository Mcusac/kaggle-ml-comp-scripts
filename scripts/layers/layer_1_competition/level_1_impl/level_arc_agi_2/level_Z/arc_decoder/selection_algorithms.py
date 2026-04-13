import numpy as np

from .scoring_core import score_sum


def getter_full_probmul_3(guesses, baseline=3):
    inf_score = np.sum([baseline - g["beam_score"] for g in guesses])
    aug_score = np.mean([
        np.sum([baseline - s for s in g["score_aug"]])
        for g in guesses
    ])
    return inf_score + aug_score


def score_full_probmul_3(guesses):
    return score_sum(guesses, getter_full_probmul_3)


def getter_kgmon(guesses):
    inf_score = len(guesses)
    aug_score = np.mean([np.mean(g["score_aug"]) for g in guesses])
    return inf_score - aug_score


def score_kgmon(guesses):
    return score_sum(guesses, getter_kgmon)


selection_algorithms = [
    score_full_probmul_3,
    score_kgmon,
]