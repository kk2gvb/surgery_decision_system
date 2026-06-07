from engine.models import Parameter, SurgeryStage, DecisionRule, Condition, Action
from engine.decision_engine import DecisionEngine
import json

def load_rules(engine: DecisionEngine):
    with open('data/rules.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for stage_data in data.get("stages", []):
        stage = SurgeryStage(name=stage_data["name"])
        engine.add_stage(stage)
        
        for rule_data in stage_data.get("rules", []):
            conditions = [Condition(**cond) for cond in rule_data["conditions"]]
            
            rule = DecisionRule(
                id=rule_data["id"],
                stage=rule_data["stage"],
                conditions=conditions,
                action=Action(**rule_data["action"]),
                risk_level=rule_data["risk_level"],
                description=rule_data.get("description", "")
            )
            engine.add_rule(rule)

def get_user_parameters(stage_name: str) -> dict:
    """Интерактивный ввод параметров для выбранного этапа"""
    print(f"\nВведите параметры для этапа: {stage_name}")
    params = {}
    
    # Разные параметры в зависимости от этапа
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
        params["разрыв_капсулы"] = Parameter("разрыв_капсулы", input("Есть разрыв капсулы? (да/нет): ").lower() == "да", type="boolean")
    
    elif stage_name == "Имплантация ИОЛ":
        params["ВГД"] = Parameter("ВГД", float(input("ВГД (мм рт.ст.): ")), "мм рт.ст.")
        params["смещение_ИОЛ"] = Parameter("смещение_ИОЛ", float(input("Смещение ИОЛ (мм): ")), "мм")
    
    elif stage_name == "Герметизация":
        params["seidel_test"] = Parameter("seidel_test", input("Тест Зейделя положительный? (да/нет): ").lower() == "да", type="boolean")
    
    elif stage_name == "Постоперационный контроль":
        params["ВГД"] = Parameter("ВГД", float(input("ВГД (мм рт.ст.): ")), "мм рт.ст.")
    
    else:
        print("Неизвестный этап.")
    
    return params

def main():
    print("=== Система поддержки принятия решений в хирургии глаза ===\n")
    
    engine = DecisionEngine()
    load_rules(engine)
    
    stages = list(engine.stages.keys())
    
    while True:
        print("\nВыберите этап операции:")
        for i, stage in enumerate(stages, 1):
            print(f"{i}. {stage}")
        print("0. Выход")
        
        try:
            choice = int(input("\nВаш выбор: "))
            if choice == 0:
                print("До свидания!")
                break
            if 1 <= choice <= len(stages):
                selected_stage = stages[choice-1]
                params = get_user_parameters(selected_stage)
                
                print(f"\n--- Результат для этапа: {selected_stage} ---")
                recommendation = engine.get_recommendation(selected_stage, params)
                print(recommendation)
            else:
                print("Неверный выбор!")
        except ValueError:
            print("Введите число!")

if __name__ == "__main__":
    main()