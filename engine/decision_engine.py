from typing import Dict, List, Optional
from .models import Parameter, DecisionRule, DecisionResult, Action, SurgeryStage
import streamlit as st

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

    def get_recommendation(self, stage_name: str, parameters: Dict[str, Parameter]) -> list:
        results = self.evaluate_stage(stage_name, parameters)
        recommendations = []
        if not results:
            return "Статус: НОРМА. Продолжайте операцию по протоколу."

        critical = [r for r in results if r.status == "критическое"]
        if critical:
            for i in range (len(critical)):
                recommendations.append(f"КРИТИЧЕСКОЕ: {critical[i].action.description}\n")

        attention = [r for r in results if r.status == "внимание"]
        if attention:
            for i in range (len(attention)):
                recommendations.append(f"ВНИМАНИЕ: {attention[i].action.description}\n")

        return recommendations

    def get_user_parameters(self, stage_name: str) -> dict:
        print(f"\nВведите параметры для этапа: {stage_name}")
        params = {}
        
        if stage_name == "Анестезия":
            params["боль"] = Parameter("боль", float(input("Оценка боли (0-5): ")))
        elif stage_name == "Разрез":
            params["длина_разреза"] = Parameter("длина_разреза", float(input("Длина разреза (мм): ")))
        elif stage_name == "Капсулорексис":
            params["диаметр_капсулорексиса"] = Parameter("диаметр_капсулорексиса", float(input("Диаметр капсулорексиса (мм): ")))
        elif stage_name == "Фрагментация ядра":
            params["CDE"] = Parameter("CDE", float(input("CDE (кДж): ")), "кДж")
            params["вакуум"] = Parameter("вакуум", float(input("Вакуум (мм рт.ст.): ")), "мм рт.ст.")
            params["температура"] = Parameter("температура", float(input("Температура наконечника (°C): ")), "°C")
        elif stage_name == "Аспирация кортекса":
            params["вакуум"] = Parameter("вакуум", float(input("Вакуум (мм рт.ст.): ")), "мм рт.ст.")
            params["разрыв_капсулы"] = Parameter("разрыв_капсулы", input("Есть разрыв капсулы? (да/нет): ").lower() == "да")
        elif stage_name == "Имплантация ИОЛ":
            params["ВГД"] = Parameter("ВГД", float(input("ВГД (мм рт.ст.): ")), "мм рт.ст.")
            params["смещение_ИОЛ"] = Parameter("смещение_ИОЛ", float(input("Смещение ИОЛ (мм): ")), "мм")
        elif stage_name == "Герметизация":
            params["seidel_test"] = Parameter("seidel_test", input("Тест Зейделя положительный? (да/нет): ").lower() == "да")
        elif stage_name == "Постоперационный контроль":
            params["ВГД"] = Parameter("ВГД", float(input("ВГД (мм рт.ст.): ")), "мм рт.ст.")
        else:
            print("Неизвестный этап.")
        
        return params
