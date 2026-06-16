from typing import Dict, List, Optional
from .models import Parameter, DecisionRule, DecisionResult, Action, SurgeryStage

class DecisionEngine:
    def __init__(self):
        self.stages: Dict[str, SurgeryStage] = {}
        self.rules: List[DecisionRule] = []

    def add_stage(self, stage: SurgeryStage):
        self.stages[stage.name] = stage

    def add_rule(self, rule: DecisionRule):
        self.rules.append(rule)
        if rule.stage in self.stages:
            self.stages[rule.stage].rules.append(rule)

    def evaluate_stage(self, stage_name: str, parameters: Dict[str, Parameter]) -> List[DecisionResult]:
        results = []
        stage = self.stages.get(stage_name)

        if not stage:
            return results

        for rule in stage.rules:
            if rule.evaluate(parameters):
                result = DecisionResult(
                    rule_id=rule.id,
                    stage=stage_name,
                    status=rule.risk_level,
                    action=rule.action,
                    triggered_conditions=[cond.description for cond in rule.conditions]
                )
                results.append(result)

        return results

    def get_recommendation(self, stage_name: str, parameters: Dict[str, Parameter]) -> str:
        results = self.evaluate_stage(stage_name, parameters)
        recommendations = ""
        if not results:
            return "Статус: НОРМА. Продолжайте операцию по протоколу."

        critical = [r for r in results if r.status == "критическое"]
        if critical:
            for i in range (len(critical)):
                recommendations += f"КРИТИЧЕСКОЕ: {critical[i].action.description}\n"

        attention = [r for r in results if r.status == "внимание"]
        if attention:
            for i in range (len(attention)):
                recommendations += f"ВНИМАНИЕ: {attention[i].action.description}\n"

        return recommendations
