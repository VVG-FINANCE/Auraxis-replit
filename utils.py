# =========================
# utils.py - Auraxis robusto
# =========================
from typing import Dict

# =========================
# Calcula Risk/Reward
# =========================
def calcular_rr(entrada: float, stop: float, take: float) -> float:
    """
    Calcula RR (Risk/Reward)
    :param entrada: preço de entrada
    :param stop: preço do stop loss
    :param take: preço do take profit
    :return: razão risco/ganho
    """
    risco = abs(entrada - stop)
    ganho = abs(take - entrada)
    if risco == 0:
        return 0
    return round(ganho / risco, 4)

# =========================
# Ajusta score combinando base + ML + Bayes
# =========================
def score_final(score_base: float, score_ml: float, peso_ml: float = 0.6) -> float:
    """
    Combina score base do candle com score do ML
    :param score_base: score inicial do candle (0–100)
    :param score_ml: score previsto pelo ML (0–100)
    :param peso_ml: influência do ML no score final
    :return: score final ajustado (0–100)
    """
    return round(score_base * (1 - peso_ml) + score_ml * peso_ml, 2)

# =========================
# Limita valores dentro de uma zona
# =========================
def limitar_valor(valor: float, zona: Dict[str, float]) -> float:
    """
    Garante que o valor esteja dentro de zona definida
    :param valor: valor a limitar
    :param zona: dict com 'inferior' e 'superior'
    :return: valor limitado
    """
    if valor < zona["inferior"]:
        return zona["inferior"]
    if valor > zona["superior"]:
        return zona["superior"]
    return valor

# =========================
# Converte pips para preço
# =========================
def pips_para_preco(preco_base: float, pips: float) -> float:
    """
    Converte pips em preço EUR/USD
    :param preco_base: preço atual
    :param pips: número de pips (positivo ou negativo)
    :return: preço ajustado
    """
    return round(preco_base + (pips * 0.0001), 5)

# =========================
# Converte preço para pips
# =========================
def preco_para_pips(preco_base: float, preco_alvo: float) -> float:
    """
    Converte diferença de preço em pips
    :param preco_base: preço de referência
    :param preco_alvo: preço alvo
    :return: pips (positivo ou negativo)
    """
    return round((preco_alvo - preco_base) / 0.0001, 2)

# =========================
# Normaliza score entre 0 e 100
# =========================
def normalizar_score(score: float) -> float:
    """
    Garante que score esteja entre 0 e 100
    """
    if score < 0:
        return 0
    if score > 100:
        return 100
    return round(score, 2)
