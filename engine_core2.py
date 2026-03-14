import time
from datetime import datetime
from candle_analysis import CandleAnalysis
from machine_learning import MLModule
from monte_carlo import MonteCarlo
from bayes import Bayes
from engine.market_state import MarketState
from utils import calcular_rr, score_final

class EngineCore:
    """
    Motor central do Auraxis
    - Consolida MarketState + CandleAnalysis + ML + Monte Carlo + Bayes
    - Gera entradas persistentes multi-trader
    - Mantém histórico de oportunidades
    """

    def __init__(self):
        self.market = MarketState()
        self.analysis = CandleAnalysis()
        self.ml_module = MLModule()
        self.monte_carlo = MonteCarlo()
        self.bayes_module = Bayes()
        self.oportunidades = []  # Histórico de entradas
        self.ajuste_pips = 0.0   # Ajuste manual para preço (±pips)

        # Tipos de traders suportados
        self.trader_types = ["scalper", "day", "swing", "position"]

    # =========================
    # Atualiza o estado do mercado
    # =========================
    def atualizar_mercado(self):
        self.market.atualizar_estado()

    # =========================
    # Gera oportunidades de trading
    # =========================
    def gerar_oportunidades(self):
        candle_atual = self.market.get_candle()
        if not candle_atual:
            return []

        # Ajusta preço com pips
        candle_atual["close"] += self.ajuste_pips

        # Gera oportunidade pelo CandleAnalysis
        opp = self.analysis.gerar_oportunidade(candle_atual)
        if not opp:
            return []

        # Retrovisor e indicadores
        retro = self.market.get_retrovisor()
        opp["retrovisor"] = retro

        # Score ML
        candle_anterior = self.market.candles[-2] if len(self.market.candles) > 1 else candle_atual
        ml_score = self.ml_module.predizer(candle_atual, candle_anterior, score_base=opp["score"])

        # Score Bayes
        self.bayes_module.atualizar_historico(True if ml_score > 50 else False)
        posterior = self.bayes_module.probabilidade_posterior()

        # Score final
        opp["score"] = score_final(ml_score, posterior*100, peso_ml=0.6)

        # Risk/Reward
        opp["rr"] = calcular_rr(opp["entrada_externa"], opp["stop"], opp["take"])

        # Persistência por trader
        for t in self.trader_types:
            opp_copy = opp.copy()
            opp_copy["trader_type"] = t
            self.oportunidades.append(opp_copy)

        # Limita histórico para 50 entradas
        if len(self.oportunidades) > 50:
            self.oportunidades = self.oportunidades[-50:]

        return self.oportunidades

    # =========================
    # Atualiza entradas persistentes
    # =========================
    def atualizar_entradas(self, preco_atual):
        """
        Remove entradas que atingiram stop ou take final
        """
        entradas_ativas = []
        for opp in self.oportunidades:
            stop_final = max(opp["stop"], opp["entrada_interna"])
            take_final = min(opp["take"], opp["entrada_interna"])
            if (preco_atual >= take_final) or (preco_atual <= stop_final):
                continue
            entradas_ativas.append(opp)
        self.oportunidades = entradas_ativas

    # =========================
    # Ajuste manual de pips
    # =========================
    def set_ajuste_pips(self, pips):
        self.ajuste_pips = pips * 0.0001  # converte pips para valor real

    # =========================
    # Retorna oportunidades ativas
    # =========================
    def get_oportunidades_ativas(self, trader_type=None):
        if trader_type:
            return [o for o in self.oportunidades if o["trader_type"] == trader_type]
        return self.oportunidades

    # =========================
    # Simulação Monte Carlo para oportunidades
    # =========================
    def calcular_probabilidades(self, preco_atual, passos=10):
        simulacoes = self.monte_carlo.simular_preco(preco_atual, passos=passos)
        resultados = []
        for opp in self.oportunidades:
            prob_take = self.monte_carlo.calcular_probabilidade_alcance(simulacoes, opp["take"])
            prob_stop = self.monte_carlo.calcular_probabilidade_alcance(simulacoes, opp["stop"])
            resultados.append({
                "tipo": opp["trader_type"],
                "entrada": opp["entrada_externa"],
                "take": opp["take"],
                "stop": opp["stop"],
                "score": opp["score"],
                "prob_take": prob_take,
                "prob_stop": prob_stop
            })
        return resultados
