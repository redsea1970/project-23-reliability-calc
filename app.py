"""
Учебный проект: калькулятор надежности ПО.
Веб-интерфейс на Streamlit.
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from models import korkoran_reliability, shumann_reliability, shumann_lambda


st.set_page_config(page_title="Калькулятор надежности ПО", page_icon="🛠️", layout="wide")

st.title("🛠️ Учебный калькулятор надежности ПО")
st.caption(
    "Pet-project по инженерии программного обеспечения. "
    "Расчёт надежности по моделям Коркорэна и Шумана. "
    "Основа: учебное пособие ТГТУ «Программирование БПЛА» (Практическая 9)."
)

tab1, tab2, tab3 = st.tabs(["Модель Коркорэна", "Модель Шумана", "О моделях"])

# ---------- Модель Коркорэна ----------
with tab1:
    st.header("Модель Коркорэна")
    st.markdown(
        "Статическая модель. Учитывает результаты $N$ прогонов программы "
        "и число отказов каждого типа $N_i$.\n\n"
        r"$$R = \frac{N_0}{N} + \sum_{i=1}^{k} a_i \cdot \frac{N_i - 1}{N}$$"
    )

    col1, col2 = st.columns(2)
    with col1:
        N = st.number_input("Общее число прогонов, N", min_value=1, value=50, step=1)
        N0 = st.number_input("Число безотказных прогонов, N0", min_value=0, value=40, step=1)
    with col2:
        st.write("Типы отказов (можно изменить):")
        # По умолчанию 3 типа отказов с разными вероятностями выявления
        default_types = {
            "Не взлетел": (3, 0.2),
            "Не выполнил команду": (5, 0.3),
            "Потеря связи": (2, 0.15),
        }
        failures_by_type = {}
        alphas = {}
        for err_type, (ni, ai) in default_types.items():
            col_a, col_b = st.columns(2)
            with col_a:
                ni_input = st.number_input(f"{err_type} (Ni)", min_value=0, value=ni, step=1, key=f"ni_{err_type}")
            with col_b:
                ai_input = st.slider(f"a_i для «{err_type}»", min_value=0.0, max_value=1.0, value=ai, step=0.05, key=f"ai_{err_type}")
            failures_by_type[err_type] = ni_input
            alphas[err_type] = ai_input

    if N0 > N:
        st.error("N0 не может быть больше N.")
    else:
        R = korkoran_reliability(N, N0, failures_by_type, alphas)
        st.metric("Вероятность безотказной работы R", f"{R:.3f}")
        if R < 0.8:
            st.warning("Надежность ниже 0.8 — рекомендуем увеличить объем тестирования.")
        elif R >= 0.95:
            st.success("Надежность высокая (≥ 0.95).")

        st.subheader("Разбор по типам отказов")
        data = {
            "Тип отказа": list(failures_by_type.keys()),
            "Ni": list(failures_by_type.values()),
            "a_i": [alphas[k] for k in failures_by_type],
            "Вклад в R": [
                alphas[k] * (failures_by_type[k] - 1) / N if failures_by_type[k] > 0 else 0.0
                for k in failures_by_type
            ],
        }
        st.dataframe(data, use_container_width=True)

# ---------- Модель Шумана ----------
with tab2:
    st.header("Модель Шумана")
    st.markdown(
        "Динамическая модель. Функция надежности экспоненциально убывает со временем "
        "работы программы без отказов.\n\n"
        r"$$R(t) = e^{-\lambda t}$$"
    )

    col1, col2 = st.columns(2)
    with col1:
        errors = st.number_input("Число ошибок за этап тестирования", min_value=0, value=10, step=1)
        time_hours = st.number_input("Длительность этапа тестирования, часы", min_value=0.1, value=10.0, step=0.5)
    with col2:
        t_max = st.number_input("Горизонт прогноза, часы", min_value=1.0, value=100.0, step=1.0)

    time_seconds = time_hours * 3600.0
    lam = shumann_lambda(errors, time_seconds)

    st.metric("Интенсивность отказов λ", f"{lam:.6f} 1/час" if time_seconds > 0 else "0")

    # График R(t)
    t = np.linspace(0, t_max, 200)
    R_vals = [shumann_reliability(tt * 3600.0, time_seconds, lam) for tt in t]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(t, R_vals, color="#1f77b4", linewidth=2)
    ax.set_xlabel("Время работы, часы")
    ax.set_ylabel("Вероятность безотказной работы R(t)")
    ax.set_title("Функция надежности (модель Шумана)")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)
    st.pyplot(fig)

    st.info(
        f"При λ = {lam:.6f} 1/час через {t_max:.1f} ч надежность составит "
        f"R = {shumann_reliability(t_max * 3600.0, time_seconds, lam):.4f}."
    )

# ---------- О моделях ----------
with tab3:
    st.header("О реализованных моделях")
    st.markdown(
        """
        ### Модель Коркорэна
        - **Тип:** статическая.
        - **Входные данные:** число прогонов $N$, число безотказных $N_0$, 
          число отказов каждого типа $N_i$, вероятности выявления $a_i$.
        - **Применение:** оценка надежности по результатам тестовых прогонов,
          когда известны типы ошибок.

        ### Модель Шумана
        - **Тип:** динамическая.
        - **Входные данные:** число ошибок на этапе, длительность этапа.
        - **Применение:** прогнозирование вероятности безотказной работы
          на заданном горизонте времени.

        ### Источники
        - Учебное пособие ТГТУ «Программирование БПЛА мультироторного типа»
          (Практическая 9, «Тестирование и расчет надежности ПО»).
        - Baez-López, Villegas. *Introduction to Python* (гл. 9, Optimization).
        """
    )
