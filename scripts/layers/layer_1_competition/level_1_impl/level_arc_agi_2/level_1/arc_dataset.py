import json

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import shuffled
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import forward_mod, invert_mod

class ArcDataset:
    """Core dataset skeleton: queries, replies, keys, I/O, submission."""

    def __init__(self, queries, replies={}, keys=None, is_orig=False):
        if keys is not None:
            keys = [k for k in keys if k is not None]
        self.queries = queries if keys is None else {k: queries[k] for k in keys}
        self.replies = replies if keys is None else {k: replies[k] for k in keys if k in replies}
        self.is_orig = is_orig
        self.keys = sorted(queries.keys()) if keys is None else keys
        self.transposed_dataset = None

    # --- loading ---
    @classmethod
    def from_file(cls, queries_file, keys=None):
        with open(queries_file) as f:
            queries = json.loads(f.read())
        return cls(queries=queries, is_orig=True, keys=keys)

    def load_replies(self, replies_file):
        print(f"*** Load solutions from '{replies_file}'...")
        with open(replies_file) as f:
            replies_parsed = json.loads(f.read())
        self.replies = {k: replies_parsed[k] for k in self.keys}
        return self

    # --- basic dataset manipulation ---
    def shuffled(self):
        return self.__class__(queries=self.queries, replies=self.replies, keys=shuffled(self.keys))

    def split_multi_replies(self):
        from arc_dataset_utils import split_multi_replies_helper
        return split_multi_replies_helper(self)

    # --- transformation helpers ---
    @staticmethod
    def forward_mod(a, key, use_perm=True):
        return forward_mod(a, key, use_perm)

    @staticmethod
    def invert_mod(a, key, inv_perm=True):
        return invert_mod(a, key, inv_perm)

    # --- submission ---
    def get_submission(self, results=None):
        from arc_dataset_utils import get_submission_helper
        return get_submission_helper(self, results)

    @staticmethod
    def fill_submission(results, submission):
        from arc_dataset_utils import fill_submission_helper
        fill_submission_helper(results, submission)

    def validate_submission(self, submission):
        from arc_dataset_utils import validate_submission_helper
        return validate_submission_helper(self, submission)