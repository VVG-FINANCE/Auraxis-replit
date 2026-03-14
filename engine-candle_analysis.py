from datetime import datetime
from config import TRADING_CONFIG
from utils import calcular_rr, limitar_valor

class CandleAnalysis:
    """
    Analisa candles e gera oportunidades robustas para o Auraxis.
    """

    def __init__(self):
        self.patterns = ["bullish_engulfing", "bearish_engulfing", "pin_bar", "hammer", "doji"]
        self.rr_min = TRADING_CONFIG["rr_min"]
        self.limites = TRADING_CONFIG["limites_zona"]
        self.ultimo_candle = None

    # =========================
    # Detecta padrões de candle
    # =========================
    def detectar_padroes(self, candle_atual, candle_anterior):
        padroes_detectados = []

        corpo_atual = abs(candle_atual["close"] - candle_atual["open"])
        corpo_anterior = abs(candle_anterior["close"] - candle_anterior["open"])

        # Bullish Engulfing
        if candle_anterior["close"] < candle_anterior["open"] and candle_atual["close"] > candle_atual["open"] and candle_atual["close"] > candle_anterior["open"]:
            padroes_detectados.append("bullish_engulfing")

        # Bearish Engulfing
        if candle_anterior["close"] > candle_anterior["open"] and candle_atual["close"] < candle_atual["open"] and candle_atual["close"] < candle_anterior["open"]:
            padroes_detectados.append("bearish_engulfing")

        # Pin Bar
        sombra_sup = candle_atual["high"] - max(candle_atual["close"], candle_atual["open"])
        sombra_inf = min(candle_atual["close"], candle_atual["open"]) - candle_atual["low"]
        if sombra_sup > 2*corpo_atual or sombra_inf > 2*corpo_atual:
            padroes_detectados.append("pin_bar")

        # Martelo
        if corpo_atual < 0.0005 and sombra_inf > 2*corpo_atual:
            padroes_detectados.append("hammer")

        # Doji
        if corpo_atual < 0.0002:
            padroes_detectados.append("doji")

        return padroes_detectados

    # =========================
    # Gera oportunidade com zona, entradas e stops
    # =========================
    def gerar_oportunidade(self, candle):
        candle_anterior = self.ultimo_candle if self.ultimo_candle else candle
        padroes = self.detectar_padroes(candle, candle_anterior)

        if not padroes:
            self.ultimo_candle = candle
            return None

        preco = candle["close"]
        tipo = "Compra" if "bullish_engulfing" in padroes or "pin_bar" in padroes else "Venda"

        # =========================
        # Entradas dupla com limites de zona
        # =========================
        zona_entrada = self.limites["entrada"]
        zona_stop = self.limites["stop"]
        zona_take = self.limites["take"]

        if tipo == "Compra":
            entrada_externa = round(preco, 5)
            entrada_interna = round(preco - (zona_entrada["inferior"] + (zona_entrada["superior"]-zona_entrada["inferior"])/2), 5)
            stop1 = round(preco - (zona_stop["inferior"] + (zona_stop["superior"]-zona_stop["inferior"])/2), 5)
            stop2 = round(preco - zona_stop["inferior"], 5)
            take1 = round(preco + (zona_take["inferior"] + (zona_take["superior"]-zona_take["inferior"])/2), 5)
            take2 = round(preco + zona_take["superior"], 5)
        else:
            entrada_externa = round(preco, 5)
            entrada_interna = round(preco + (zona_entrada["inferior"] + (zona_entrada["superior"]-zona_entrada["inferior"])/2), 5)
            stop1 = round(preco + (zona_stop["inferior"] + (zona_stop["superior"]-zona_stop["inferior"])/2), 5)
            stop2 = round(preco + zona_stop["superior"], 5)
            take1 = round(preco - (zona_take["inferior"] + (zona_take["superior"]-zona_take["inferior"])/2), 5)
            take2 = round(preco - zona_take["superior"], 5)

        # Calcula RR mínimo
        rr = calcular_rr(entrada_externa, stop1, take1)
        if rr < self.rr_min:
            self.ultimo_candle = candle
            return None

        # Score inicial simplificado
        score_base = 80 if "bullish_engulfing" in padroes or "bearish_engulfing" in padroes else 70

        # Tendência
        tendencia = "A favor" if (tipo=="Compra" and preco >= candle_anterior["close"]) or (tipo=="Venda" and preco <= candle_anterior["close"]) else "Contra"

        oportunidade = {
            "id": f"{datetime.now().timestamp()}_{tipo}",  # ID único
            "tipo": tipo,
            "entrada1": entrada_externa,
            "entrada2": entrada_interna,
            "stop1": stop1,
            "stop2": stop2,
            "take1": take1,
            "take2": take2,
            "rr": round(rr,2),
            "score_base": score_base,
            "score_final": score_base,   # será atualizado por ML/Bayes
            "tendencia": tendencia,
            "padroes": padroes,
            "time": datetime.now().isoformat()
        }

        self.ultimo_candle = candle
        return oportunidade
