from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class ParameterType(Enum):
    NUMERIC = "numeric"
    BOOLEAN = "boolean"
    STRING = "string"

@dataclass
class Parameter:
    name: str
    value: Any
    unit: str = ""
    type: ParameterType = ParameterType.NUMERIC
    description: str = ""

@dataclass
class Condition:
    parameter: str
    operator: str      # ">", "<", ">=", "<=", "==", "!="
    value: Any
    description: str = ""

    def check(self, params: Dict[str, Parameter]) -> bool:
        if self.parameter not in params:
            return False
        pval = params[self.parameter].value

        if self.operator == ">":   return pval > self.value
        elif self.operator == "<": return pval < self.value
        elif self.operator == ">=": return pval >= self.value
        elif self.operator == "<=": return pval <= self.value
        elif self.operator in ["==", "="]: return pval == self.value
        elif self.operator == "!=": return pval != self.value
        return False

@dataclass
class Action:
    description: str
    code: str = ""

@dataclass
class DecisionRule:
    id: str
    stage: str
    conditions: List[Condition]
    action: Action
    risk_level: str   # "норма", "внимание", "критическое"
    description: str = ""

    def evaluate(self, params: Dict[str, Parameter]) -> bool:
        return all(cond.check(params) for cond in self.conditions)

@dataclass
class DecisionResult:
    rule_id: str
    stage: str
    status: str
    action: Action
    triggered_conditions: List[str] = None

class SurgeryStage:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.parameters: Dict[str, Parameter] = {}
        self.rules: List[DecisionRule] = []