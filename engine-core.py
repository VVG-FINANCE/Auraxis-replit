import time
from threading import Thread
from data_manager import DataManager
from candle_analysis import CandleAnalysis
from ml_module import MLModule
from monte_carlo import MonteCarlo
from datetime import datetime

class EngineCore:
    """
    Motor central do simulador Auraxis
    - Integra dados reais, candle analysis, ML, Monte Carlo
    - Suporta múltiplos tipos de trader: scalper, day, swing, position
    - Mantém histórico e score adaptativo
    """

    def __init__(self):
        self.data_manager = DataManager()
        self.candle_analysis = CandleAnalysis()
        self.ml_module = MLModule()
        self.monte_carlo = MonteCarlo(n_simulations=1000)
        self.oportunidades = {"scalper": [], "day": [], "swing": [], "position": []}
        self.historico_candles = []
        self.running = True
        self.intervalo_atual = 5  # segundos, ajustável dinamicamente

    # =========================
    # Loop de atualização contínua
    # =========================
    def iniciar_loop(self):
        def loop():
            while self.running:
                try:
                    self.atualizar_candles()
                    self.gerar_oportunidades()
                    time.sleep(self.intervalo_atual)
                except Exception as e:
                    print("Erro no loop do motor:", e)
                    time.sleep(10)  # pausa se erro crítico
        Thread(target=loop, daemon=True).start()

    # =========================
    # Atualiza candles do mercado
    # =========================
    def atualizar_candles(self, n=100):
        candles = self.data_manager.obter_candles(n)
        self.historico_candles = candles[-n:]

        # Labels fictícios: 1=Compra, 0=Venda (para treino inicial)
        labels = [1 if i % 2 == 0 else 0 for i in range(len(candles))]
        self.ml_module.treinar(candles, labels)

    # =========================
    # Gera oportunidades reais
    # =========================
    def gerar_oportunidades(self):
        candle_atual = self.historico_candles[-1]
        candle_anterior = self.historico_candles[-2]

        # Gera oportunidade básica pelo candle
        opp = self.candle_analysis.gerar_oportunidade(candle_atual)
        if not opp:
            return

        # Ajusta score via ML + Bayes
        score_final = self.ml_module.predizer(candle_atual, candle_anterior, opp["score_base"])
        opp["score_final"] = score_final

        # Distribui por tipo de trader
        for trader_type in self.oportunidades.keys():
            self.oportunidades[trader_type].append(opp)

        # Limita histórico
        for trader_type in self.oportunidades.keys():
            if len(self.oportunidades[trader_type]) > 50:
                self.oportunidades[trader_type].pop(0)

    # =========================
    # Simula cenários futuros via Monte Carlo
    # =========================
    def simular_futuros(self, passos=10):
        preco_atual = self.data_manager.obter_preco_atual()
        simulacoes = self.monte_carlo.simular_preco(preco_atual, passos=passos)
        return simulacoes

    # =========================
    # Calcula probabilidade de atingir níveis de preço
    # =========================
    def probabilidade_alcance(self, nivel):
        simulacoes = self.simular_futuros()
        prob = self.monte_carlo.calcular_probabilidade_alcance(simulacoes, nivel)
        return prob

    # =========================
    # Permite ajuste manual de pips
    # =========================
    def ajustar_preco_manual(self, pips=0.0):
        """
        Adiciona ou subtrai pips ao último preço para calibragem
        """
        if not self.historico_candles:
            return
        ajuste = pips * 0.0001  # 1 pip = 0.0001 EUR/USD
        self.historico_candles[-1]["close"] += ajuste
        self.historico_candles[-1]["open"] += ajuste
        self.historico_candles[-1]["high"] += ajuste
        self.historico_candles[-1]["low"] += ajuste

    # =========================
    # Recupera oportunidades recentes
    # =========================
    def obter_oportunidades(self, trader_type="scalper", n=10):
        return self.oportunidades.get(trader_type, [])[-n:]
