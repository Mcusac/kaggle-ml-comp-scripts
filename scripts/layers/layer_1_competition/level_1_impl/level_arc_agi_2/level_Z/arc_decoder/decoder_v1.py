from .decoded_loader import load_decoded_results_into
from .selection_algorithms import score_kgmon
from .benchmarking_v1 import benchmark_selection_algos_v1


class ArcDecoder:
    
    def __init__(self, dataset, n_guesses):
        self.dataset = dataset
        self.n_guesses = n_guesses
        self.decoded_results = {}

    def load_decoded_results(self, store, run_name=""):
        load_decoded_results_into(
            self.decoded_results,
            store,
            run_name
        )

    def run_selection_algo(self, selection_algorithm=score_kgmon):
        return {
            bk: selection_algorithm({k: g for k, g in v.items()})
            for bk, v in self.decoded_results.items()
        }

    def benchmark_selection_algos(self):
        benchmark_selection_algos_v1(
            decoded_results=self.decoded_results,
            dataset=self.dataset,
            n_guesses=self.n_guesses,
            run_selection_algo=self.run_selection_algo,
        )