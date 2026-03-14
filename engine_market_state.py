import numpy as np
from datetime import datetime

class MarketState:
    """
    MarketState central: mantém candles, indicadores multitimeframe,
    oportunidades, histórico de trades, score médio e volatilidade.
    """

    def __init__(self):
        # Preço atual do EUR/USD
        self.preco_atual = None

        # Candles multitimeframe: dicionário com timeframe -> lista de candles
        self.candles = {
            "1m": [],
            "5m": [],
            "15m": [],
        }

        # Indicadores calculados
        self.indicadores = {
            "sma": {},         # média móvel simples
            "ema": {},         # média móvel exponencial
            "std": {},         # desvio padrão
            "volatilidade": 0, # volatilidade recente
        }

        # Eventos institucionais detectados
        self.eventos_institucionais = []

        # Oportunidades ativas (entradas atuais)
        self.oportunidades_ativas = []

        # Histórico completo de trades
        self.historico_trades = []

    # =========================
    # Atualiza candles por timeframe
    # =========================
    def update_candles(self, candles_multitimeframe):
        """
        Recebe candles de múltiplos timeframes e atualiza o estado.
        candles_multitimeframe: dict {"1m":[...], "5m":[...], "15m":[...]}
        """
        for tf, candles in candles_multitimeframe.items():
            if tf not in self.candles:
                self.candles[tf] = []
            self.candles[tf].extend(candles)
            # Limita histórico para os últimos 200 candles por timeframe
            if len(self.candles[tf]) > 200:
                self.candles[tf] = self.candles[tf][-200:]

    # =========================
    # Calcula indicadores multitimeframe
    # =========================
    def calcular_indicadores(self):
        for tf, candles in self.candles.items():
            closes = [c["close"] for c in candles]
            if len(closes) < 2:
                continue

            # SMA simples
            self.indicadores["sma"][tf] = np.mean(closes[-20:])

            # EMA exponencial
            self.indicadores["ema"][tf] = self._calcular_ema(closes, periodo=20)

            # Desvio padrão
            self.indicadores["std"][tf] = np.std(closes[-20:])

        # Volatilidade aproximada baseada em 1m
        if self.candles["1m"]:
            closes = np.array([c["close"] for c in self.candles["1m"]])
            self.indicadores["volatilidade"] = np.std(np.diff(closes))

    # =========================
    # EMA simples
    # =========================
    def _calcular_ema(self, closes, periodo=20):
        closes = np.array(closes[-periodo:])
        if len(closes) == 0:
            return 0
        alpha = 2 / (periodo + 1)
        ema = closes[0]
        for price in closes[1:]:
            ema = alpha * price + (1 - alpha) * ema
        return ema

    # =========================
    # Atualiza eventos institucionais
    # =========================
    def update_eventos_institucionais(self, eventos):
        """
        Recebe lista de eventos institucionais detectados
        e mantém histórico limitado.
        """
        self.eventos_institucionais.extend(eventos)
        if len(self.eventos_institucionais) > 100:
            self.eventos_institucionais = self.eventos_institucionais[-100:]

    # =========================
    # Atualiza oportunidades
    # =========================
    def update_oportunidades(self, oportunidades):
        """
        Recebe oportunidades geradas e adiciona às ativas
        mantendo persistência até atingir SL ou TP final.
        """
        for opp in oportunidades:
            # Verifica se já existe oportunidade idêntica
            if not any(o["id"] == opp["id"] for o in self.oportunidades_ativas):
                self.oportunidades_ativas.append(opp)

    # =========================
    # Atualiza status das oportunidades ativas
    # =========================
    def atualizar_status_entradas(self):
        novas_ativas = []
        for opp in self.oportunidades_ativas:
            preco = self.preco_atual

            # Checa se atingiu SL ou TP final
            sls = [opp.get("stop1"), opp.get("stop2")]
            tps = [opp.get("take1"), opp.get("take2")]

            atingiu = any((preco <= sl if opp["tipo"]=="Compra" else preco >= sl) for sl in sls if sl) \
                      or any((preco >= tp if opp["tipo"]=="Compra" else preco <= tp) for tp in tps if tp)

            if not atingiu:
                novas_ativas.append(opp)
            else:
                # Move para histórico
                opp["fechado_em"] = datetime.now().isoformat()
                self.historico_trades.append(opp)

        self.oportunidades_ativas = novas_ativas

    # =========================
    # Retorna snapshot para front-end
    # =========================
    def to_dict(self):
        score_medio = 0
        if self.oportunidades_ativas:
            score_medio = np.mean([o.get("score_final",0) for o in self.oportunidades_ativas])

        return {
            "preco_atual": self.preco_atual,
            "volatilidade_atual": self.indicadores.get("volatilidade",0),
            "score_medio": round(score_medio,2),
            "oportunidades_ativas": self.oportunidades_ativas,
            "indicadores": self.indicadores,
            "eventos_institucionais": self.eventos_institucionais
        }

    # =========================
    # Retorna oportunidades ativas
    # =========================
    def get_oportunidades_ativas(self):
        return self.oportunidades_ativas

    # =========================
    # Retorna histórico de trades
    # =========================
    def get_historico_trades(self):
        return self.historico_trades
