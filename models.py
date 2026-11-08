"""
Учебный проект: калькулятор надежности ПО.
Pet-project по инженерии программного обеспечения.

Реализованы две модели:
- Модель Коркорэна (статическая, по числу отказов разных типов).
- Модель Шумана (динамическая, по интенсивности отказов на интервалах тестирования).

Основа: учебное пособие ТГТУ «Программирование БПЛА» (Практическая 9)
и книга Baez-López «Introduction to Python» (гл. 9, Optimization).
"""
import math


def korkoran_reliability(N: int, N0: int, failures_by_type: dict, alphas: dict) -> float:
    """
    Модель Коркорэна.

    Параметры:
        N (int): общее число прогонов программы.
        N0 (int): число безотказных прогонов.
        failures_by_type (dict): {тип_ошибки: количество_отказов} (Ni).
        alphas (dict): {тип_ошибки: вероятность_выявления} (a_i).

    Формула:
        R = N0/N + sum_i [ a_i * (Ni - 1) / N ]  для Ni > 0
        R = N0/N                                  для Ni = 0

    Возвращает:
        float: вероятность безотказной работы (в долях от 1).
    """
    R = N0 / N
    for err_type, Ni in failures_by_type.items():
        if Ni > 0:
            ai = alphas.get(err_type, 0.0)
            R += ai * (Ni - 1) / N
    return R


def shumann_reliability(t: float, tau: float, lambda_obs: float) -> float:
    """
    Модель Шумана (упрощенная, для функции надежности).

    Параметры:
        t (float): время работы программы без отказа (от t=0).
        tau (float): длительность этапа тестирования.
        lambda_obs (float): наблюдаемая интенсивность отказов
                            (число ошибок в единицу времени на этапе тестирования).

    Формула:
        R(t, tau) = exp(-lambda_obs * t)
    """
    return math.exp(-lambda_obs * t)


def shumann_lambda(errors: int, time_seconds: float) -> float:
    """
    Вычисляет наблюдаемую интенсивность отказов λ.

    Параметры:
        errors (int): число ошибок, обнаруженных за этап.
        time_seconds (float): длительность этапа тестирования (сек).

    Возвращает:
        float: интенсивность отказов (1/сек).
    """
    if time_seconds <= 0:
        return 0.0
    return errors / time_seconds
