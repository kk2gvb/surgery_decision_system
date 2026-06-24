import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import json
import random
import time

from engine.models import Parameter, SurgeryStage, DecisionRule, Condition, Action
from engine.decision_engine import DecisionEngine
from simulator.scenario_generator import ScenarioGenerator

# ====================== ЗАГРУЗКА ПРАВИЛ ======================
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


# ====================== ИНИЦИАЛИЗАЦИЯ ======================
if 'engine' not in st.session_state:
    st.session_state.engine = DecisionEngine()
    load_rules(st.session_state.engine)

if 'generator' not in st.session_state:
    st.session_state.generator = ScenarioGenerator(st.session_state.engine)

st.set_page_config(page_title="Хирургический Тренажёр", layout="wide")
st.title("Система поддержки принятия решений в офтальмохирургии")
st.markdown("**Факоэмульсификация катаракты** — учебный прототип")

tabs = st.tabs(["Обычная проверка", "Режим Тренажёра", "Все правила"])

# ====================== ВКЛАДКА 1: Обычная проверка ======================
with tabs[0]:
    st.header("Обычная проверка параметров")

    stages = list(st.session_state.engine.stages.keys())
    stage_name = st.selectbox("Выберите этап операции", stages)
 
    params = {}

    if stage_name == "Анестезия":
        params["боль"] = st.number_input("Оценка боли (0-5)", value=0, step=1)
    elif stage_name == "Разрез":
        params["длина_разреза"] = st.number_input("Длина_разреза(мм)", value=0.0, step=0.1)
    elif stage_name == "Капсулорексис":
        params["диаметр_капсулорексиса"] = st.number_input("Диаметр капсулорексиса (мм)", value=0.0, step=0.1)
    elif stage_name == "Фрагментация ядра":
        col1, col2, col3 = st.columns(3)
        with col1:
            params["CDE"] = st.number_input("CDE (кДж)", value=20.0, step=0.1)
        with col2:
            params["вакуум"] = st.number_input("Вакуум (мм рт.ст.)", value=400, step=10)
        with col3:
            params["температура"] = st.number_input("Температура (°C)", value=36.0, step=0.1)
    elif stage_name == "Аспирация кортекса":
        params["вакуум"] = st.number_input("Вакуум (мм рт.ст.)", value=400, step=10)
        params["разрыв_капсулы"] = st.checkbox("Есть разрыв капсулы? (да/нет)", value=False)
    elif stage_name == "Имплантация ИОЛ":
        col1, col2 = st.columns(2)
        with col1:
            params["ВГД"] = st.number_input("ВГД (мм рт.ст.)", value=0, step=10)
        with col2:
            params["смещение_ИОЛ"] = st.number_input("Смещение ИОЛ (мм)", value=0.0, step=0.1)
    elif stage_name == "Герметизация":
        params["seidel_test"] = st.checkbox("Тест Зейделя положительный? (да/нет)", value=False)
    elif stage_name == "Постоперационный контроль":
        params["ВГД"] = st.number_input("ВГД (мм рт.ст.)", value=0, step=10)

    if st.button("Проверить параметры", type="primary"):
        param_objects = {k: Parameter(k, v) for k, v in params.items()}
        result = st.session_state.engine.get_recommendation(stage_name, param_objects)
        for res in result:
            if "КРИТИЧЕСКОЕ" in res:
                st.error(res)
            elif "ВНИМАНИЕ" in res:
                st.warning(res)
            else:
                st.success(res)
# ====================== ВКЛАДКА 2: Режим Тренажёра ======================
with tabs[1]:
    st.header("Режим Тренажёра")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        num_scenarios = st.slider("Количество сценариев", min_value=5, max_value=15, value=10)
        use_predefined = st.checkbox("Использовать готовые сценарии", value=True)
    
    if st.button("Сгенерировать сценарии", type="primary"):
        st.session_state.training_scenarios = []
        st.session_state.user_answers = {}
        
        for i in range(num_scenarios):
            if use_predefined:
                scenario = st.session_state.generator.get_predefined_scenario()
            else:
                scenario = st.session_state.generator.generate_random_scenario()
            
            st.session_state.training_scenarios.append(scenario)
            st.session_state.user_answers[i] = None  # Пока нет ответа
    
    # Показываем сценарии
    if 'training_scenarios' in st.session_state and st.session_state.training_scenarios:
        st.subheader("Выберите ответы на все сценарии")
        
        for i, scenario in enumerate(st.session_state.training_scenarios):
            with st.expander(f"Сценарий {i+1}", expanded=True):
                st.write(f"**Этап:** {scenario['stage']}")
                st.write("**Параметры:**")
                for k, v in scenario["parameters"].items():
                    st.write(f"  {k}: **{v}**")
                
                # Формируем варианты действий
                stage = st.session_state.engine.stages.get(scenario["stage"])
                actions = ["Продолжить без изменений"]
                if stage:
                    for rule in stage.rules:
                        if rule.action.description not in actions:
                            actions.append(rule.action.description)
                
                # Выбор ответа
                answer = st.radio(
                    "Ваш выбор:",
                    options=actions,
                    key=f"answer_{i}",
                    horizontal=False
                )
                st.session_state.user_answers[i] = answer
        
        # Общая кнопка проверки
        if st.button("Проверить все ответы", type="primary"):
            correct_count = 0
            results = []
            
            for i, scenario in enumerate(st.session_state.training_scenarios):
                user_answer = st.session_state.user_answers.get(i)
                is_correct = user_answer == scenario["correct_action"]
                
                if is_correct:
                    correct_count += 1
                
                results.append({
                    "scenario_num": i+1,
                    "stage": scenario["stage"],
                    "user_answer": user_answer,
                    "correct_answer": scenario["correct_action"],
                    "is_correct": is_correct,
                    "explanation": scenario["explanation"]
                })
            
            accuracy = (correct_count / len(st.session_state.training_scenarios)) * 100
            
            st.success(f"### Итоги тренировки\nПравильных ответов: **{correct_count}** из **{len(results)}** ({accuracy:.1f}%)")
            
            for res in results:
                if res["is_correct"]:
                    st.success(f"**Сценарий {res['scenario_num']}** — Правильно")
                else:
                    st.error(f"**Сценарий {res['scenario_num']}** — Неверно")
                    st.info(f"Правильный ответ: **{res['correct_answer']}**")
                st.caption(f"Пояснение: {res['explanation']}")
                st.divider()
    
    else:
        st.info("Нажмите кнопку «Сгенерировать сценарии», чтобы начать тренировку.")

# ====================== ВКЛАДКА 3: Все правила системы ======================

with tabs[2]:
    st.header("Все правила системы")
    for stage_name, stage in st.session_state.engine.stages.items():
        with st.expander(f"Этап: **{stage_name}**"):
            for rule in stage.rules:
                st.write(f"**{rule.id}** — {rule.description}")
                st.write(f"**Действие:** {rule.action.description}")
                st.write(f"Уровень риска: **{rule.risk_level}**")
                st.divider()

