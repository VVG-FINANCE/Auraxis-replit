# =========================
# history_manager.py - Auraxis robusto
# =========================
import json
import os
from datetime import datetime
from typing import List, Dict

class HistoryManager:
    """
    Gerencia o histórico completo das oportunidades
    - Persistência em JSON para memória do sistema
    - Integra com Bayes e Monte Carlo
    - Suporta múltiplos tipos de trader (scalper, day, swing, position)
    """

    def __init__(self, filepath: str = "history.json"):
        self.filepath = filepath
        self.oportunidades: List[Dict] = []
        self.carregar_historico()

    # =========================
    # Carrega histórico do arquivo
    # =========================
    def carregar_historico(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.oportunidades = json.load(f)
            except Exception:
                self.oportunidades = []
        else:
            self.oportunidades = []

    # =========================
    # Salva histórico no arquivo
    # =========================
    def salvar_historico(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.oportunidades, f, indent=4, default=str)
        except Exception as e:
            print(f"[HistoryManager] Erro ao salvar histórico: {e}")

    # =========================
    # Adiciona nova oportunidade
    # =========================
    def adicionar_oportunidade(self, opp: Dict):
        """
        Adiciona oportunidade ao histórico
        opp deve conter:
        {
            'tipo': 'Compra'/'Venda',
            'trader_type': 'scalper'/'day'/'swing'/'position',
            'entrada_externa': float,
            'entrada_interna': float,
            'stop1': float,
            'stop2': float,
            'take1': float,
            'take2': float,
            'score': float,
            'score_ml': float,
            'score_bayes': float,
            'tendencia': str,
            'padroes': list,
            'time': timestamp,
            'status': 'ativo'/'finalizado'
        }
        """
        self.oportunidades.append(opp)
        self.salvar_historico()

    # =========================
    # Atualiza status de oportunidade
    # =========================
    def atualizar_status(self, opp_time: str, status: str):
        """
        Atualiza status de oportunidade pelo timestamp
        """
        for opp in self.oportunidades:
            if opp["time"] == opp_time:
                opp["status"] = status
                self.salvar_historico()
                return True
        return False

    # =========================
    # Retorna oportunidades recentes
    # =========================
    def obter_oportunidades(self, n: int = 10, tipo_trader: str = None) -> List[Dict]:
        """
        Retorna últimas n oportunidades, filtrando por tipo de trader se informado
        """
        filtradas = self.oportunidades
        if tipo_trader:
            filtradas = [o for o in filtradas if o.get("trader_type") == tipo_trader]

        return filtradas[-n:]

    # =========================
    # Retorna oportunidades ativas
    # =========================
    def obter_ativas(self, tipo_trader: str = None) -> List[Dict]:
        """
        Retorna todas as oportunidades ainda ativas (não atingiram stop/take)
        """
        filtradas = [o for o in self.oportunidades if o.get("status") == "ativo"]
        if tipo_trader:
            filtradas = [o for o in filtradas if o.get("trader_type") == tipo_trader]
        return filtradas

    # =========================
    # Atualiza score Bayes de uma oportunidade
    # =========================
    def atualizar_score_bayes(self, opp_time: str, score_bayes: float):
        """
        Atualiza score ajustado pelo Bayes
        """
        for opp in self.oportunidades:
            if opp["time"] == opp_time:
                opp["score_bayes"] = score_bayes
                self.salvar_historico()
                return True
        return False

    # =========================
    # Limpa histórico antigo
    # =========================
    def reset_historico(self):
        self.oportunidades = []
        self.salvar_historico()
