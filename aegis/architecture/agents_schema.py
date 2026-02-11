from dataclasses import dataclass
from typing import Dict, List

@dataclass
class AgentNode:
    name: str
    inputs: List[str]
    outputs: List[str]

@dataclass
class AgentGraph:
    nodes: Dict[str, AgentNode]
    edges: List[List[str]]

def default_graph():
    nodes = {
        "digital_twin": AgentNode("digital_twin", ["csv", "income", "debt", "emi"], ["forecast", "default_prob"]),
        "risk": AgentNode("risk", ["forecast"], ["heatmap", "intervention"]),
        "bank": AgentNode("bank", ["risk"], ["offer"]),
        "compliance": AgentNode("compliance", ["offer"], ["flags"]),
        "fairness": AgentNode("fairness", ["offer"], ["parity"])
    }
    edges = [
        ["digital_twin", "risk"],
        ["risk", "bank"],
        ["bank", "compliance"],
        ["bank", "fairness"]
    ]
    return AgentGraph(nodes=nodes, edges=edges)
