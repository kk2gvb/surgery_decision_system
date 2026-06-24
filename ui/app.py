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
    engine = DecisionEngine()

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
    st.info("Полноценный тренажёр с таймером и статистикой удобнее использовать через консоль (`python main.py`)")

# ====================== ВКЛАДКА 4: Все правила ======================
with tabs[2]:
    st.header("Все правила системы")
    for stage_name, stage in st.session_state.engine.stages.items():
        with st.expander(f"Этап: **{stage_name}**"):
            for rule in stage.rules:
                st.write(f"**{rule.id}** — {rule.description}")
                st.write(f"→ **Действие:** {rule.action.description}")
                st.write(f"Уровень риска: **{rule.risk_level}**")
                st.divider()

