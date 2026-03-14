# =========================
# monte_carlo.py - Auraxis robusto
# =========================
import numpy as np

class MonteCarlo:
    """
    Simulação de Monte Carlo para prever caminhos futuros de preço EUR/USD.
    Permite calcular probabilidades de atingir níveis de preço, stops e takes.
    """

    def __init__(self, n_simulations=1000, passos=20, volatilidade=0.001):
        """
        :param n_simulations: número de simulações a executar
        :param passos: número de passos futuros a simular (ex: 20 = 20 minutos se candle 1 min)
        :param volatilidade: desvio padrão da variação percentual por passo
        """
        self.n_simulations = n_simulations
        self.passos = passos
        self.volatilidade = volatilidade

    # =========================
    # Simula caminhos futuros
    # =========================
    def simular_preco(self, preco_atual):
        """
        Gera múltiplos caminhos futuros do preço usando Monte Carlo
        :param preco_atual: preço base
        :return: array (n_simulations x passos+1) com cada simulação
        """
        resultados = np.zeros((self.n_simulations, self.passos + 1))
        resultados[:, 0] = preco_atual

        for i in range(self.n_simulations):
            for j in range(1, self.passos + 1):
                # Movimento percentual baseado em normal distribution
                movimento = np.random.normal(0, self.volatilidade)
                resultados[i, j] = resultados[i, j - 1] * (1 + movimento)

        return resultados

    # =========================
    # Calcula probabilidade de atingir um nível
    # =========================
    def calcular_probabilidade_alcance(self, simulacoes, nivel):
        """
        Calcula a probabilidade de que qualquer ponto das simulações alcance ou ultrapasse o nível.
        :param simulacoes: array retornado por simular_preco()
        :param nivel: nível de preço (take ou stop)
        :return: probabilidade (0 a 1)
        """
        count = np.sum(simulacoes >= nivel)
        total = simulacoes.size
        prob = count / total
        return round(prob, 4)

    # =========================
    # Calcula probabilidade de não atingir o nível
    # =========================
    def calcular_probabilidade_nao_alcance(self, simulacoes, nivel):
        """
        Probabilidade de o preço NÃO atingir determinado nível
        """
        count = np.sum(simulacoes < nivel)
        total = simulacoes.size
        prob = count / total
        return round(prob, 4)

    # =========================
    # Retorna métricas de cada simulação
    # =========================
    def estatisticas_simulacao(self, simulacoes):
        """
        Retorna média, desvio padrão e máximos/mínimos das simulações
        :param simulacoes: array de simulações
        :return: dict com estatísticas
        """
        medias = np.mean(simulacoes, axis=0)
        desvios = np.std(simulacoes, axis=0)
        maximos = np.max(simulacoes, axis=0)
        minimos = np.min(simulacoes, axis=0)
        return {
            "media": medias.tolist(),
            "desvio": desvios.tolist(),
            "maximo": maximos.tolist(),
            "minimo": minimos.tolist()
        }
