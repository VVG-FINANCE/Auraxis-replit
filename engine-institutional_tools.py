import numpy as np
import pandas as pd
from scipy.stats import entropy
from scipy.stats import linregress


class InstitutionalTools:

    def __init__(self):
        pass

    # ==========================================
    # REGIME DE MERCADO
    # ==========================================

    def detect_market_regime(self, prices):

        if len(prices) < 50:
            return "unknown"

        prices = np.array(prices)

        returns = np.diff(prices)

        volatility = np.std(returns)

        # regressão linear para medir tendência
        x = np.arange(len(prices))
        slope, _, r_value, _, _ = linregress(x, prices)

        trend_strength = abs(slope) * abs(r_value)

        if volatility > np.mean(np.abs(returns)) * 3:
            return "volatile"

        if trend_strength > volatility:
            return "trending"

        return "ranging"

    # ==========================================
    # DETECÇÃO DE FLUXO INSTITUCIONAL
    # ==========================================

    def detect_institutional_flow(self, candles):

        if len(candles) < 20:
            return False

        ranges = []
        bodies = []

        for c in candles:
            high = c["high"]
            low = c["low"]
            open_ = c["open"]
            close = c["close"]

            ranges.append(high - low)
            bodies.append(abs(close - open_))

        ranges = np.array(ranges)
        bodies = np.array(bodies)

        avg_range = np.mean(ranges[:-1])
        last_range = ranges[-1]

        avg_body = np.mean(bodies[:-1])
        last_body = bodies[-1]

        if last_range > avg_range * 2 and last_body > avg_body * 1.5:
            return True

        return False

    # ==========================================
    # HURST EXPONENT
    # ==========================================

    def hurst_exponent(self, prices):

        prices = np.array(prices)

        if len(prices) < 100:
            return 0.5

        lags = range(2, 30)

        tau = []

        for lag in lags:

            diff = np.subtract(prices[lag:], prices[:-lag])
            tau.append(np.sqrt(np.std(diff)))

        tau = np.array(tau)

        poly = np.polyfit(np.log(lags), np.log(tau), 1)

        hurst = poly[0] * 2

        return float(hurst)

    # ==========================================
    # ENTROPIA DE MERCADO
    # ==========================================

    def market_entropy(self, prices):

        prices = np.array(prices)

        if len(prices) < 20:
            return 0

        returns = np.diff(prices)

        hist, _ = np.histogram(returns, bins=15, density=True)

        hist = hist + 1e-9

        ent = entropy(hist)

        max_ent = np.log(len(hist))

        normalized_entropy = ent / max_ent

        return float(normalized_entropy)

    # ==========================================
    # DETECTOR DE SHOCK DE LIQUIDEZ
    # ==========================================

    def detect_liquidity_shock(self, prices):

        if len(prices) < 30:
            return False

        returns = np.diff(prices)

        std = np.std(returns)

        last_move = abs(returns[-1])

        if last_move > std * 4:
            return True

        return False

    # ==========================================
    # VOLATILITY CLUSTERING
    # ==========================================

    def volatility_clustering(self, prices):

        if len(prices) < 50:
            return 0

        returns = np.diff(prices)

        vol = np.abs(returns)

        corr = np.corrcoef(vol[:-1], vol[1:])[0, 1]

        if np.isnan(corr):
            corr = 0

        return float(corr)

    # ==========================================
    # ACELERAÇÃO DE PREÇO
    # ==========================================

    def price_acceleration(self, prices):

        if len(prices) < 10:
            return 0

        returns = np.diff(prices)

        accel = returns[-1] - returns[-2]

        return float(accel)

    # ==========================================
    # SCORE INSTITUCIONAL
    # ==========================================

    def institutional_score(self, prices, candles):

        score = 0

        regime = self.detect_market_regime(prices)

        flow = self.detect_institutional_flow(candles)

        hurst = self.hurst_exponent(prices)

        ent = self.market_entropy(prices)

        shock = self.detect_liquidity_shock(prices)

        clustering = self.volatility_clustering(prices)

        accel = self.price_acceleration(prices)

        # regime

        if regime == "trending":
            score += 5

        if regime == "volatile":
            score += 3

        # fluxo institucional

        if flow:
            score += 10

        # hurst

        if hurst > 0.6:
            score += 5

        if hurst > 0.7:
            score += 5

        # entropia

        if ent < 0.7:
            score += 5

        if ent < 0.5:
            score += 5

        # choque de liquidez

        if shock:
            score += 5

        # clustering

        if clustering > 0.5:
            score += 4

        # aceleração

        if abs(accel) > np.std(np.diff(prices)) * 2:
            score += 3

        return min(score, 25)
