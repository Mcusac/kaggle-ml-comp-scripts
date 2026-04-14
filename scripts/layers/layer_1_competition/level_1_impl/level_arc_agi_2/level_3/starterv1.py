from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import run_entry
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import worker_v1

run_entry(
    worker_fn=worker_v1,
    nprocs=2,
    test_filter=["0934a4d8", "36a08778", "981571dc", "aa4ec2a5"],
)