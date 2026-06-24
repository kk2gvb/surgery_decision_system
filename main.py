from engine.models import Parameter, SurgeryStage, DecisionRule, Condition, Action
from engine.decision_engine import DecisionEngine
from simulator.scenario_generator import ScenarioGenerator
import random
import time
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

def trainer_mode(engine, generator, use_predefined=False):
    print(f"\n=== РЕЖИМ ТРЕНАЖЁРА {'(ГОТОВЫЕ СЦЕНАРИИ)' if use_predefined else '(СЛУЧАЙНЫЕ СЦЕНАРИИ)'} ===")
    print("Будет 10 сценариев.\n")
    
    total = 10
    correct = 0
    start_time = time.time()
    
    for i in range(1, total + 1):
        print(f"\n--- Сценарий {i}/{total} ---")
        
        if use_predefined:
            scenario = generator.get_predefined_scenario()
        else:
            scenario = generator.generate_random_scenario()
        
        stage_name = scenario["stage"]
        
        print(f"Этап: {stage_name}")
        print("Параметры:")
        for key, value in scenario["parameters"].items():
            print(f"   {key}: {value}")
        
        # Формируем варианты ответов
        stage = engine.stages.get(stage_name)
        actions = ["Продолжить без изменений"]
        if stage:
            for rule in stage.rules:
                if rule.action.description not in actions:
                    actions.append(rule.action.description)
        
        random.shuffle(actions)
        
        print("\nВыберите правильное действие:")
        for idx, action in enumerate(actions, 1):
            print(f"{idx}. {action}")
        
        try:
            user_input = int(input("\nВаш выбор: "))
            selected = actions[user_input - 1]
            
            if selected == scenario["correct_action"]:
                print("ПРАВИЛЬНО!")
                correct += 1
            else:
                print("НЕВЕРНО")
                print(f"Правильное действие: {scenario['correct_action']}")
            
            print(f"Пояснение: {scenario['explanation']}\n")
            
        except:
            print("Ошибка ввода → неверно\n")
    
    total_time = round(time.time() - start_time, 1)
    accuracy = (correct / total) * 100
    
    print("\n" + "="*60)
    print("                  ИТОГИ ТРЕНИРОВКИ")
    print("="*60)
    print(f"Всего сценариев:     {total}")
    print(f"Правильных ответов:  {correct}")
    print(f"Точность:            {accuracy:.1f}%")
    print(f"Общее время:         {total_time} сек")
    print("="*60)


def normal_mode(engine):
    stages = list(engine.stages.keys())
    print("\nВыберите этап:")
    for i, s in enumerate(stages, 1):
        print(f"{i}. {s}")
    
    try:
        idx = int(input("\nНомер этапа: ")) - 1
        stage_name = stages[idx]
        params = engine.get_user_parameters(stage_name)
        recommendation = engine.get_recommendation(stage_name, params)
        print(f"\n--- Результат для этапа {stage_name} ---")
        print(recommendation)
    except Exception as e:
        print(f"Ошибка ввода: {e}")


def main():
    print("=== Система поддержки принятия решений в хирургии глаза ===\n")
    
    engine = DecisionEngine()
    load_rules(engine)
    generator = ScenarioGenerator(engine=engine)
    
    while True:
        print("\nВыберите режим:")
        print("1. Обычная проверка параметров")
        print("2. Тренажёр — Случайные сценарии")
        print("3. Тренажёр — Готовые сценарии (из scenarios.json)")
        print("0. Выход")
        
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "0":
            print("До свидания!")
            break
        elif choice == "1":
            normal_mode(engine)
        elif choice == "2":
            trainer_mode(engine, generator, use_predefined=False)
        elif choice == "3":
            trainer_mode(engine, generator, use_predefined=True)
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main()
