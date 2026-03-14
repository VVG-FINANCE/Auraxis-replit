# =========================
# quantitative_tools.py - Auraxis robusto
# =========================
import numpy as np
import pandas as pd
from pmdarima.arima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model

class QuantitativeTools:
    """
    Ferramentas matemáticas e financeiras:
    - Previsão de preço (ARIMA/GARCH)
    - Filtro de Kalman
    - Simulações complementares de Monte Carlo
    - Métricas de risco (Sharpe, Drawdown, etc.)
    """

    def __init__(self):
        self.kalman_state = None
        self.kalman_cov = None

    # =========================
    # Filtro de Kalman simples para preço
    # =========================
    def kalman_filter(self, prices: list):
        """
        Aplica Kalman Filter unidimensional simples
        """
        n = len(prices)
        if n == 0:
            return []
        x_hat = np.zeros(n)
        P = np.zeros(n)
        Q = 1e-5  # processo de variância
        R = 1e-2  # medição de variância
        x_hat[0] = prices[0]
        P[0] = 1.0
        for k in range(1, n):
            # Predição
            x_pred = x_hat[k-1]
            P_pred = P[k-1] + Q
            # Atualização
            K = P_pred / (P_pred + R)
            x_hat[k] = x_pred + K * (prices[k] - x_pred)
            P[k] = (1 - K) * P_pred
        self.kalman_state = x_hat[-1]
        self.kalman_cov = P[-1]
        return x_hat

    # =========================
    # Previsão ARIMA
    # =========================
    def prever_arima(self, prices: list, passos: int = 1):
        """
        Previsão de preço usando ARIMA automático
        """
        if len(prices) < 20:
            return None
        try:
            model = auto_arima(prices, seasonal=False, stepwise=True, suppress_warnings=True)
            forecast = model.predict(n_periods=passos)
            return forecast
        except Exception:
            return None

    # =========================
    # Previsão GARCH (volatilidade)
    # =========================
    def prever_garch(self, returns: list, passos: int = 1):
        """
        Previsão de volatilidade com GARCH(1,1)
        """
        if len(returns) < 20:
            return None
        try:
            model = arch_model(returns, vol='Garch', p=1, q=1)
            model_fit = model.fit(disp='off')
            forecast = model_fit.forecast(horizon=passos)
            return forecast.variance.values[-1]
        except Exception:
            return None

    # =========================
    # Simulação de Monte Carlo complementar
    # =========================
    def monte_carlo_simulation(self, preco_atual: float, passos: int = 10, n_simulations: int = 1000, volatilidade: float = 0.001):
        """
        Simula caminhos futuros de preço usando Monte Carlo
        """
        resultados = []
        for _ in range(n_simulations):
            precos = [preco_atual]
            for _ in range(passos):
                movimento = np.random.normal(0, volatilidade)
                preco_novo = precos[-1] * (1 + movimento)
                precos.append(preco_novo)
            resultados.append(precos)
        return np.array(resultados)

    # =========================
    # Probabilidade de atingir nível
    # =========================
    def probabilidade_alcance(self, simulacoes: np.ndarray, nivel: float):
        """
        Calcula probabilidade de atingir determinado nível
        """
        count = np.sum(simulacoes >= nivel)
        total = simulacoes.size
        return round(count / total, 4)

    # =========================
    # Métricas de risco
    # =========================
    def calcular_sharpe(self, returns: list, risk_free_rate: float = 0.0):
        """
        Sharpe ratio anualizado
        """
        if len(returns) < 2:
            return 0
        mean = np.mean(returns) - risk_free_rate
        std = np.std(returns)
        if std == 0:
            return 0
        sharpe = mean / std * np.sqrt(252)
        return sharpe

    def calcular_drawdown(self, prices: list):
        """
        Calcula drawdown máximo
        """
        prices = np.array(prices)
        peak = np.maximum.accumulate(prices)
        drawdown = (prices - peak) / peak
        max_drawdown = drawdown.min()
        return max_drawdown

    def calcular_sortino(self, returns: list, risk_free_rate: float = 0.0):
        """
        Sortino ratio anualizado
        """
        returns = np.array(returns)
        downside = returns[returns < 0]
        std_down = np.std(downside) if len(downside) > 0 else 0
        mean = np.mean(returns) - risk_free_rate
        if std_down == 0:
            return 0
        sortino = mean / std_down * np.sqrt(252)
        return sortino

    # =========================
    # Ajuste de score quantitativo
    # =========================
    def ajustar_score_quant(self, score_base: float, sharpe: float = 0, drawdown: float = 0, sortino: float = 0):
        """
        Ajusta score baseado em métricas quantitativas
        """
        ajuste = 0.0
        if sharpe > 1:
            ajuste += 5
        if drawdown < -0.05:
            ajuste -= 5
        if sortino > 1:
            ajuste += 3
        score_ajustado = max(0, min(100, score_base + ajuste))
        return score_ajustado
