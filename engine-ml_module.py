import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from engine.bayes_module import BayesModule
from utils import score_final

class MLModule:
    """
    Módulo de aprendizado do Auraxis
    - Treina modelo baseado em candles passados
    - Prediz score e confiança de oportunidades
    """

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=150, random_state=42)
        self.scaler = StandardScaler()
        self.trained = False
        self.history = []         # Histórico de treinamento
        self.bayes = BayesModule() # Bayes adaptativo para score
        self.weight_ml = 0.6      # Peso do ML na composição do score final

    # =========================
    # Extrai features de candle
    # =========================
    def extrair_features(self, candle, candle_anterior, indicadores=None):
        corpo = candle["close"] - candle["open"]
        range_candle = candle["high"] - candle["low"]
        delta = candle["close"] - candle_anterior["close"]

        features = [
            candle["open"], candle["high"], candle["low"], candle["close"],
            candle_anterior["open"], candle_anterior["high"], candle_anterior["low"], candle_anterior["close"],
            corpo, range_candle, delta
        ]

        # Adiciona indicadores multitimeframe se fornecido
        if indicadores:
            for tf in ["1m", "5m", "15m"]:
                features.append(indicadores["sma"].get(tf, 0))
                features.append(indicadores["ema"].get(tf, 0))
                features.append(indicadores["std"].get(tf, 0))
                features.append(indicadores.get("volatilidade", 0))

        return np.array(features)

    # =========================
    # Treina o modelo
    # =========================
    def treinar(self, candles, labels, indicadores=None):
        X = []
        y = []
        for i in range(1, len(candles)):
            X.append(self.extrair_features(candles[i], candles[i-1], indicadores))
            y.append(labels[i])
        X = np.array(X)
        y = np.array(y)

        # Normaliza
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.trained = True

        # Armazena histórico
        self.history = {"X": X_scaled.tolist(), "y": y.tolist()}

    # =========================
    # Prediz score para uma oportunidade
    # =========================
    def predizer(self, candle, candle_anterior, score_base=80, indicadores=None):
        if not self.trained:
            return score_base

        features = self.extrair_features(candle, candle_anterior, indicadores).reshape(1, -1)
        features_scaled = self.scaler.transform(features)

        prob = self.model.predict_proba(features_scaled)[0]
        score_ml = round(max(prob) * 100, 2)

        # Ajusta via Bayes adaptativo
        posterior = self.bayes.probabilidade_posterior()
        score_ajustado = score_final(score_base, score_ml, peso_ml=self.weight_ml)
        score_final_completo = round(score_ajustado * posterior, 2)

        return score_final_completo

    # =========================
    # Atualiza histórico Bayes
    # =========================
    def atualizar_bayes(self, acerto):
        """
        acerto: True se trade foi acertado, False se errado
        """
        self.bayes.atualizar_historico(acerto)
