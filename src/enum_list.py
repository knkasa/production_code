from enum import Enum

class SYSTEMS(Enum):
    mode = 'local'

class LIGHTGBM(Enum):
    n_trials = 3
    test_size = 0.1
    seed = 123
