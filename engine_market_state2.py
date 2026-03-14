import numpy as np
from datetime import datetime
from data_manager import DataManager

class MarketState:
    """
    Mantém o estado vivo do mercado EUR/USD
    - Histórico de candles
    - Indicadores técnicos multi-timeframe
    - EMA, Kalman Filter, desvios
    - Tendência de mercado
    - Retrovisor para alimentar o motor central
    """

    def __init__(self):
        self.data_manager = DataManager()
        self.candles = []          # Lista de candles completos
        self.indicadores = {}      # EMA, desvios, kalman
        self.timeframes = [1, 5, 15, 60]  # minutos para retrovisor
        self.kalman_estimate = None
        self.kalman_error = 1.0
        self.kalman_process = 1e-5
        self.kalman_measure = 0.01

    # =========================
    # Atualiza candles e indicadores
    # =========================
    def atualizar_estado(self):
        # Gera candle do DataManager
        candle = self.data_manager.gerar_candle()
        self.candles.append(candle)
        if len(self.candles) > 500:
            self.candles.pop(0)

        # Atualiza EMA multi-timeframe
        for tf in self.timeframes:
            self.calcular_ema(tf)

        # Atualiza Kalman filter
        self.calcular_kalman(candle["close"])

        # Atualiza desvios padrão
        self.calcular_desvios()

    # =========================
    # EMA simples
    # =========================
    def calcular_ema(self, periodo):
        closes = [c["close"] for c in self.candles[-periodo:]]
        if not closes:
            return
        ema = closes[0]
        alpha = 2 / (periodo + 1)
        for price in closes[1:]:
            ema = alpha * price + (1 - alpha) * ema
        self.indicadores[f"EMA_{periodo}"] = ema

    # =========================
    # Kalman Filter simples
    # =========================
    def calcular_kalman(self, measurement):
        if self.kalman_estimate is None:
            self.kalman_estimate = measurement
            return self.kalman_estimate
        # Predição
        pred_error = self.kalman_error + self.kalman_process
        # Ganho de Kalman
        K = pred_error / (pred_error + self.kalman_measure)
        # Atualiza estimativa
        self.kalman_estimate = self.kalman_estimate + K * (measurement - self.kalman_estimate)
        # Atualiza erro
        self.kalman_error = (1 - K) * pred_error
        return self.kalman_estimate

    # =========================
    # Desvio padrão e bandas
    # =========================
    def calcular_desvios(self, periodo=20):
        closes = [c["close"] for c in self.candles[-periodo:]]
        if len(closes) < 2:
            return
        media = np.mean(closes)
        desvio = np.std(closes)
        self.indicadores[f"media_{periodo}"] = media
        self.indicadores[f"desvio_{periodo}"] = desvio
        self.indicadores[f"upper_{periodo}"] = media + 2*desvio
        self.indicadores[f"lower_{periodo}"] = media - 2*desvio

    # =========================
    # Tendência simples baseada em EMA e Kalman
    # =========================
    def get_trend(self):
        trend = "Neutra"
        if not self.indicadores:
            return trend
        # Comparar EMA 5 vs EMA 15
        ema5 = self.indicadores.get("EMA_5")
        ema15 = self.indicadores.get("EMA_15")
        kalman = self.kalman_estimate
        if ema5 and ema15:
            if ema5 > ema15 and kalman > ema5:
                trend = "Alta"
            elif ema5 < ema15 and kalman < ema5:
                trend = "Baixa"
        return trend

    # =========================
    # Retorna candle mais recente
    # =========================
    def get_candle(self):
        return self.candles[-1] if self.candles else None

    # =========================
    # Retorna indicadores atuais
    # =========================
    def get_indicators(self):
        return self.indicadores

    # =========================
    # Retrovisor multi-timeframe (para ML e Score)
    # =========================
    def get_retrovisor(self):
        retro = {}
        for tf in self.timeframes:
            retro[f"EMA_{tf}"] = self.indicadores.get(f"EMA_{tf}")
        retro["Kalman"] = self.kalman_estimate
        retro["Trend"] = self.get_trend()
        return retro
