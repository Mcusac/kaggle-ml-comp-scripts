import numpy as np

def split_multi_replies_helper(dataset):
    key_indices = [(k, i) for k in dataset.keys for i in range(len(dataset.queries[k]['test']))]
    return dataset.__class__(
        keys=[f'{k}_{i}' for k, i in key_indices],
        queries={f'{k}_{i}': {'train': dataset.queries[k]['train'], 'test': [dataset.queries[k]['test'][i]]} for k, i in key_indices},
        replies={f'{k}_{i}': [dataset.replies[k][i]] for k, i in key_indices if k in dataset.replies},
    )

def get_submission_helper(dataset, results=None):
    assert dataset.is_orig, 'Must be run on original dataset.'
    submission = {
        k: [{f'attempt_{i+1}': [[0]] for i in range(2)}
            for _ in range(len(dataset.queries[k]['test']))]
        for k in dataset.keys
    }
    if results:
        fill_submission_helper(results, submission)
    return submission

def fill_submission_helper(results, submission):
    print(f'*** Generating submission for {len(results)} outputs...')
    for k, v in results.items():
        base_id, base_nr = k.split('_')
        target_dict = submission[base_id][int(base_nr)]
        for i, g in enumerate(v[:len(target_dict)]):
            target_dict[f'attempt_{i+1}'] = g.tolist()

def validate_submission_helper(dataset, submission):
    assert dataset.is_orig, 'Must be run on original dataset.'
    score = 0
    for k, v in dataset.replies.items():
        for i, r in enumerate(v):
            for attempt in ['attempt_1', 'attempt_2']:
                if np.array_equal(r, submission[k][i][attempt]):
                    score += 1 / len(v)
                    break
    return score
