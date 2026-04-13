import numpy as np
from .selection_algorithms import selection_algorithms


def benchmark_selection_algos(
    decoded_results,
    dataset,
    n_guesses,
    run_selection_algo,
):
    print("*** Benchmark selection algorithms...")

    labels = {}
    num_tasks_per_puzzle = {}
    num_solved_keys = 0
    num_total_keys = 0

    correct_beam_scores = []

    for basekey, basevalues in decoded_results.items():

        mult_key, mult_sub = basekey.split("_")
        num_tasks_per_puzzle[mult_key] = max(
            num_tasks_per_puzzle.get(mult_key, 0),
            int(mult_sub) + 1
        )

        labels[basekey] = correct_solution = dataset.replies[basekey][0]

        for subkey, sample in basevalues.items():

            solution = sample["solution"]
            beam_score = sample["beam_score"]
            aug_mean = np.mean(sample["score_aug"])

            if np.shape(correct_solution) != np.shape(solution):
                corr_str = "bad_xy_size"
            elif np.array_equal(correct_solution, solution):
                corr_str = "ALL_CORRECT"
                num_solved_keys += 1
                correct_beam_scores.append(beam_score)
            else:
                corr_str = "bad_content"

            output_len = f"{solution.shape[0]}x{solution.shape[1]}"

            if corr_str == "ALL_CORRECT":
                print(
                    f"{corr_str}:{beam_score:8.5f} - "
                    f"{aug_mean:8.5f} {output_len:5s} [{subkey}]"
                )

            num_total_keys += 1

    print(f" subkeys: {num_solved_keys}/{num_total_keys}")
    print(f" avg correct beam score: {np.mean(correct_beam_scores):8.5f}")
    print(f" max correct beam score: {np.max(correct_beam_scores):8.5f}")

    num_puzzles = len(num_tasks_per_puzzle)

    for selection_algorithm in selection_algorithms:
        name = selection_algorithm.__name__

        selected = run_selection_algo(selection_algorithm)

        correct_puzzles = {
            k for k, v in selected.items()
            if any(
                np.array_equal(guess, labels[k])
                for guess in v[:n_guesses]
            )
        }

        print(correct_puzzles)

        score = sum(
            1 / num_tasks_per_puzzle[k.split("_")[0]]
            for k in correct_puzzles
        )

        print(f" acc: {score:5.1f}/{num_puzzles:3} ('{name}')")