import json
import random
from typing import Dict, List, Optional
from engine.models import Parameter
from engine.decision_engine import DecisionEngine

class ScenarioGenerator:
    def __init__(self, engine: Optional[DecisionEngine] = None):
        self.engine = engine
        self.predefined_scenarios = self._load_predefined_scenarios()

    def _load_predefined_scenarios(self) -> List[Dict]:
        try:
            with open('data/scenarios.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("scenarios", [])
        except FileNotFoundError:
            return []
        except Exception:
            return []

    def generate_random_scenario(self, stage_name: str = None) -> Dict:
        """Генерирует случайный сценарий"""
        if not stage_name:
            stage_name = random.choice(self.get_available_stages())

        params = self._generate_parameters(stage_name)
        
        # Определяем правильное действие через движок
        results = self.engine.evaluate_stage(stage_name, params) if self.engine else []
        
        if results:
            critical = [r for r in results if r.status == "критическое"]
            top = critical[0] if critical else results[0]
            correct_action = top.action.description
            explanation = top.triggered_conditions[0] if top.triggered_conditions else "Сработало правило"
            risk_level = top.status
        else:
            correct_action = "Продолжить без изменений"
            explanation = "Все параметры в пределах нормы"
            risk_level = "normal"

        return {
            "id": f"rand_{random.randint(10000, 99999)}",
            "stage": stage_name,
            "parameters": {k: v.value for k, v in params.items()},
            "risk_level": risk_level,
            "correct_action": correct_action,
            "explanation": explanation,
            "params_full": params,
            "is_predefined": False
        }

    def get_predefined_scenario(self) -> Dict:
        """Возвращает готовый сценарий из файла"""
        if not self.predefined_scenarios:
            return self.generate_random_scenario()
        scenario = random.choice(self.predefined_scenarios)
        scenario["is_predefined"] = True
        return scenario

    def _generate_parameters(self, stage_name: str) -> Dict[str, Parameter]:
        params = {}
        
        if stage_name == "Анестезия":
            params["боль"] = Parameter("боль", random.randint(0, 5))
        
        elif stage_name == "Разрез":
            params["длина_разреза"] = Parameter("длина_разреза", round(random.uniform(1.8, 4.2), 2), "мм")
        
        elif stage_name == "Капсулорексис":
            params["диаметр_капсулорексиса"] = Parameter("диаметр_капсулорексиса", round(random.uniform(3.0, 7.5), 2), "мм")
        
        elif stage_name == "Фрагментация ядра":
            params["CDE"] = Parameter("CDE", round(random.uniform(5, 52), 2), "кДж")
            params["вакуум"] = Parameter("вакуум", random.randint(120, 820), "мм рт.ст.")
            params["температура"] = Parameter("температура", round(random.uniform(32, 48), 1), "°C")
        
        elif stage_name == "Аспирация кортекса":
            params["вакуум"] = Parameter("вакуум", random.randint(70, 550), "мм рт.ст.")
            params["разрыв_капсулы"] = Parameter("разрыв_капсулы", random.choice([True, False]))
        
        elif stage_name == "Имплантация ИОЛ":
            params["ВГД"] = Parameter("ВГД", random.randint(6, 45), "мм рт.ст.")
            params["смещение_ИОЛ"] = Parameter("смещение_ИОЛ", round(random.uniform(0.0, 2.8), 2), "мм")
        
        elif stage_name == "Герметизация":
            params["seidel_test"] = Parameter("seidel_test", random.choice([True, False]))
        
        elif stage_name == "Постоперационный контроль":
            params["ВГД"] = Parameter("ВГД", random.randint(3, 48), "мм рт.ст.")
        
        return params

    def get_available_stages(self) -> List[str]:
        """Все этапы из rules.json"""
        return [
            "Анестезия", "Разрез", "Капсулорексис", "Фрагментация ядра",
            "Аспирация кортекса", "Имплантация ИОЛ", "Герметизация", 
            "Постоперационный контроль"
        ]
