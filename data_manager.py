import os
import time
import requests
import yfinance as yf
from datetime import datetime

class DataManager:
    """
    Gerencia múltiplas fontes públicas de preço EUR/USD
    - ExchangeRate-API
    - Frankfurter API
    - yfinance fallback
    - Média exponencial
    - Fallback adaptativo com intervalos dinâmicos
    """

    def __init__(self):
        # Chaves e configurações
        self.exchangerate_key = os.environ.get("EXCHANGE_RATE_KEY", "YOUR_EXCHANGERATE_KEY")
        self.fallback_yf = True
        self.historico_precos = []
        self.alpha = 0.3  # peso da média exponencial
        self.intervalo_base = 5  # segundos
        self.intervalo_atual = self.intervalo_base
        self.max_intervalo = 60

    # =========================
    # Obtém preço ExchangeRate-API
    # =========================
    def obter_preco_exchangerate(self):
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.exchangerate_key}/latest/EUR"
            r = requests.get(url, timeout=5)
            data = r.json()
            preco = float(data['conversion_rates']['USD'])
            return preco
        except:
            return None

    # =========================
    # Obtém preço Frankfurter
    # =========================
    def obter_preco_frankfurter(self):
        try:
            url = "https://api.frankfurter.app/latest?from=EUR&to=USD"
            r = requests.get(url, timeout=5)
            data = r.json()
            preco = float(data['rates']['USD'])
            return preco
        except:
            return None

    # =========================
    # Fallback yfinance
    # =========================
    def obter_preco_yfinance(self):
        try:
            ticker = yf.Ticker("EURUSD=X")
            data = ticker.history(period="1d", interval="1m")
            preco = float(data['Close'].iloc[-1])
            return preco
        except:
            return None

    # =========================
    # Coleta preço com fallback adaptativo
    # =========================
    def obter_preco_atual(self):
        fontes = [
            self.obter_preco_exchangerate,
            self.obter_preco_frankfurter,
            self.obter_preco_yfinance if self.fallback_yf else lambda: None
        ]

        preco_final = None
        for func in fontes:
            preco = func()
            if preco is not None:
                preco_final = preco
                break

        # Ajusta média exponencial
        if preco_final is not None:
            if not self.historico_precos:
                ema = preco_final
            else:
                ema = self.alpha * preco_final + (1 - self.alpha) * self.historico_precos[-1]
            self.historico_precos.append(ema)
            if len(self.historico_precos) > 200:
                self.historico_precos.pop(0)
            self.intervalo_atual = self.intervalo_base  # reset do intervalo após sucesso
            return ema

        # Caso falha: aumenta intervalo (exponencial progressivo)
        self.intervalo_atual = min(self.intervalo_atual + 5, self.max_intervalo)
        if self.historico_precos:
            return self.historico_precos[-1]
        else:
            return 1.16100  # fallback interno inicial

    # =========================
    # Retorna histórico de candles simplificado
    # =========================
    def gerar_candle(self):
        preco = self.obter_preco_atual()
        candle = {
            "open": self.historico_precos[-2] if len(self.historico_precos) > 1 else preco,
            "high": max(preco, self.historico_precos[-2]) if len(self.historico_precos) > 1 else preco,
            "low": min(preco, self.historico_precos[-2]) if len(self.historico_precos) > 1 else preco,
            "close": preco,
            "time": datetime.now().isoformat()
        }
        return candle

    # =========================
    # Últimos n candles
    # =========================
    def obter_candles(self, n=100):
        while len(self.historico_precos) < n:
            candle = self.gerar_candle()
            time.sleep(self.intervalo_atual)
        candles = []
        for i in range(len(self.historico_precos[-n:])):
            preco = self.historico_precos[-n:][i]
            candles.append({
                "open": preco,
                "high": preco,
                "low": preco,
                "close": preco,
                "time": datetime.now().isoformat()
            })
        return candles
