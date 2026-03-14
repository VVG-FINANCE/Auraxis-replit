# =========================
# advanced_market_analysis.py - Auraxis robusto
# =========================
import numpy as np
import pandas as pd

class AdvancedMarketAnalysis:
    """
    Análise avançada do mercado:
    - Indicadores multi-timeframe
    - Econofísica: fat-tail, clusters de liquidez, desvios
    - Sinais de movimentos institucionais
    """

    def __init__(self):
        self.multi_timeframes = ["1min", "5min", "15min", "1h"]
        self.indicadores = {}
        self.historico_candles = {tf: [] for tf in self.multi_timeframes}

    # =========================
    # Atualiza candles por timeframe
    # =========================
    def atualizar_candles(self, timeframe: str, candles: list):
        """
        candles: lista de dicts com open, high, low, close, volume, time
        """
        if timeframe not in self.multi_timeframes:
            raise ValueError(f"Timeframe {timeframe} não suportado")
        self.historico_candles[timeframe] = candles[-200:]  # guarda últimos 200 candles

    # =========================
    # Indicadores multi-timeframe
    # =========================
    def calcular_ema(self, timeframe: str, period: int = 20):
        """
        Calcula EMA para fechamento dos candles
        """
        candles = self.historico_candles[timeframe]
        closes = [c["close"] for c in candles]
        if len(closes) < period:
            return None
        ema = pd.Series(closes).ewm(span=period, adjust=False).mean().tolist()
        self.indicadores[f"EMA_{period}_{timeframe}"] = ema[-1]
        return ema[-1]

    def calcular_rsi(self, timeframe: str, period: int = 14):
        """
        RSI baseado em fechamento
        """
        candles = self.historico_candles[timeframe]
        closes = [c["close"] for c in candles]
        if len(closes) < period + 1:
            return None
        delta = np.diff(closes)
        gain = np.maximum(delta, 0)
        loss = np.abs(np.minimum(delta, 0))
        avg_gain = pd.Series(gain).rolling(window=period).mean().iloc[-1]
        avg_loss = pd.Series(loss).rolling(window=period).mean().iloc[-1]
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        self.indicadores[f"RSI_{period}_{timeframe}"] = rsi
        return rsi

    def calcular_bollinger(self, timeframe: str, period: int = 20, std_dev: float = 2):
        """
        Banda de Bollinger
        """
        candles = self.historico_candles[timeframe]
        closes = [c["close"] for c in candles]
        if len(closes) < period:
            return None, None, None
        series = pd.Series(closes)
        ma = series.rolling(period).mean().iloc[-1]
        std = series.rolling(period).std().iloc[-1]
        upper = ma + std_dev * std
        lower = ma - std_dev * std
        self.indicadores[f"Bollinger_{period}_{timeframe}"] = (upper, ma, lower)
        return upper, ma, lower

    # =========================
    # Detecção de movimentos institucionais (econofísica)
    # =========================
    def detectar_movimento_institucional(self, timeframe: str, threshold_std: float = 2.0):
        """
        Detecta movimentos extremos de preço ou volume
        """
        candles = self.historico_candles[timeframe]
        if len(candles) < 20:
            return False
        closes = np.array([c["close"] for c in candles])
        mean = closes.mean()
        std = closes.std()
        last = closes[-1]
        # Se o preço se afastou mais que threshold*std, considera movimento institucional
        if abs(last - mean) > threshold_std * std:
            return True
        return False

    # =========================
    # Fat-tail e clusters de liquidez
    # =========================
    def calcular_fat_tail(self, timeframe: str):
        """
        Retorna z-score do último candle
        """
        candles = self.historico_candles[timeframe]
        closes = np.array([c["close"] for c in candles])
        if len(closes) < 20:
            return 0
        mean = closes.mean()
        std = closes.std()
        last = closes[-1]
        z_score = (last - mean) / std if std > 0 else 0
        return z_score

    # =========================
    # Consolida sinais de múltiplos indicadores
    # =========================
    def consolidar_sinais(self):
        """
        Consolida sinais de EMA, RSI, Bollinger, movimento institucional e fat-tail
        Retorna um dicionário pronto para alimentar o EngineCore e o score
        """
        sinais = {}
        for tf in self.multi_timeframes:
            ema = self.calcular_ema(tf)
            rsi = self.calcular_rsi(tf)
            boll = self.calcular_bollinger(tf)
            movimento = self.detectar_movimento_institucional(tf)
            fat_tail = self.calcular_fat_tail(tf)
            sinais[tf] = {
                "EMA": ema,
                "RSI": rsi,
                "Bollinger": boll,
                "movimento_institucional": movimento,
                "fat_tail": fat_tail
            }
        return sinais

    # =========================
    # Ajuste de score baseado nos sinais avançados
    # =========================
    def ajustar_score(self, score_base: float, sinais: dict):
        """
        Ajusta score de oportunidade baseado em indicadores avançados
        """
        ajuste = 0.0
        for tf, dados in sinais.items():
            if dados["movimento_institucional"]:
                ajuste += 5
            if dados["fat_tail"] > 2:
                ajuste += 5
            if dados["RSI"] is not None:
                if dados["RSI"] < 30:
                    ajuste += 3
                elif dados["RSI"] > 70:
                    ajuste -= 3
            if dados["EMA"] is not None:
                # Simples ajuste: preço acima da EMA aumenta score, abaixo diminui
                ultimo_close = self.historico_candles[tf][-1]["close"]
                if ultimo_close > dados["EMA"]:
                    ajuste += 2
                else:
                    ajuste -= 2
        score_ajustado = max(0, min(100, score_base + ajuste))
        return score_ajustado
