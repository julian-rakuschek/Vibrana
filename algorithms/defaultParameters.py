from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class DWTCustomParameters:
    start_level: int = 3
    quantile_epsilon: float = 0.01
    random_state: int = 42
    use_column_index: int = 0
