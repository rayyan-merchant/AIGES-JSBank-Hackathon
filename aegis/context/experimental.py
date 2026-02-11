from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Context:
    parties: Dict[str, Any]
    policies: Dict[str, Any]
    parameters: Dict[str, Any]

def default_context():
    return Context(
        parties={"borrower": {"risk": 0.2}, "bank": {"threshold": 0.5}},
        policies={"rate_cap": 0.24, "tenure_max": 60},
        parameters={"shock": 0.0, "gamma": 0.99}
    )
