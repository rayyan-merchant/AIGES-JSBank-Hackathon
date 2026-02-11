from dataclasses import dataclass
from typing import List, Dict

@dataclass
class StateSpec:
    variables: List[str]
    bounds: Dict[str, float]

@dataclass
class ActionSpec:
    variables: List[str]
    bounds: Dict[str, float]

@dataclass
class TransitionSpec:
    horizon: int
    discount: float
