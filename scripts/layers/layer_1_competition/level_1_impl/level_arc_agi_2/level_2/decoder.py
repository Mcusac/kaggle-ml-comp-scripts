from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    infer_load_decoded_results_from_dir,
    ensemble_score_kgmon,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    benchmark_selection_algos,
)


class ArcDecoder:
    def __init__(self, dataset, n_guesses):
        self.dataset = dataset
        self.n_guesses = n_guesses
        self.decoded_results = {}

    def load_decoded_results(self, store: str, run_name: str = "") -> None:
            self.decoded_results = infer_load_decoded_results_from_dir(store, run_name)

    def run_selection_algo(self, selection_algorithm=ensemble_score_kgmon):
        return {
            bk: selection_algorithm({k: g for k, g in v.items()})
            for bk, v in self.decoded_results.items()
        }

    def benchmark_selection_algos(self):
        benchmark_selection_algos(
            decoded_results=self.decoded_results,
            dataset=self.dataset,
            n_guesses=self.n_guesses,
            run_selection_algo=self.run_selection_algo,
        )