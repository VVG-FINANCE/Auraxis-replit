# =========================
# bayes.py - Auraxis robusto
# =========================
import numpy as np

class Bayes:
    """
    Ajuste probabilístico de score usando Estatística Bayesiana
    - Calcula probabilidade posterior P(H|E)
    - Permite melhorar o score das entradas conforme histórico
    """

    def __init__(self):
        self.prior_score = 0.5       # Probabilidade inicial (não enviesada)
        self.historico = []           # Histórico de acertos/falhas (True/False)

    # =========================
    # Adiciona observação ao histórico
    # =========================
    def atualizar_historico(self, evento_sucesso: bool):
        """
        :param evento_sucesso: True se entrada atingiu take, False se stop
        """
        self.historico.append(evento_sucesso)

    # =========================
    # Calcula probabilidade posterior (Bayes simples)
    # =========================
    def probabilidade_posterior(self) -> float:
        """
        Retorna P(H|E) usando Laplace smoothing
        :return: probabilidade entre 0 e 1
        """
        if not self.historico:
            return self.prior_score

        n_sucesso = sum(self.historico)
        n_total = len(self.historico)
        posterior = (n_sucesso + 1) / (n_total + 2)  # Laplace smoothing
        return round(posterior, 4)

    # =========================
    # Ajusta score com probabilidade Bayesiana
    # =========================
    def ajustar_score(self, score_base: float) -> float:
        """
        Combina score base com probabilidade posterior
        :param score_base: score inicial (0–100)
        :return: score ajustado (0–100)
        """
        posterior = self.probabilidade_posterior()
        score_ajustado = round(score_base * posterior, 2)
        return score_ajustado

    # =========================
    # Limpa histórico
    # =========================
    def reset_historico(self):
        self.historico = []
