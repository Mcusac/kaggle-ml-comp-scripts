import os
import bz2
import pickle


def load_decoded_results_into(decoded_results, store, run_name=""):
    for key in os.listdir(store):
        with bz2.BZ2File(os.path.join(store, key)) as f:
            outputs = pickle.load(f)

        base_key = key.split(".")[0]
        decoded_results[base_key] = decoded_results.get(base_key, {})

        for i, sample in enumerate(outputs):
            decoded_results[base_key][f"{key}{run_name}.out{i}"] = sample