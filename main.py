import flet as ft
import yfinance as yf
import pandas as pd
import numpy as np
import threading
import time
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# ==========================================
# 🧠 MOTOR QUANTUM AURAXIS - INTEGRAÇÃO TOTAL
# ==========================================
class AuraxisCore:
    def __init__(self):
        self.offset = 0.0000 
        self.confianca_bayes = 0.5
        self.memoria_ticks = []
        self.detector_anomalia = IsolationForest(contamination=0.1)
        self.banca_referencia = 1000.0

    def simular_monte_carlo(self, preco_atual, vol_estimada):
        """[SPRINT FINAL] Simulação de 100 caminhos para os próximos 30s"""
        simulacoes = 100
        passos = 6 
        reversoes = 0
        for _ in range(simulacoes):
            caminho = preco_atual
            for _ in range(passos):
                caminho += np.random.normal(0, vol_estimada)
            if (preco_atual > caminho): reversoes += 1
        return reversoes / simulacoes

    def analisar_padrao_ml(self, p_atual):
        """[SPRINT 2] Machine Learning para detectar Smart Money"""
        self.memoria_ticks.append(p_atual)
        if len(self.memoria_ticks) > 60: self.memoria_ticks.pop(0)
        
        if len(self.memoria_ticks) < 30: return "ANALISANDO..."
        
        fluxo = np.diff(self.memoria_ticks).reshape(-1, 1)
        self.detector_anomalia.fit(fluxo)
        pred = self.detector_anomalia.predict([[fluxo[-1][0]]])
        return "INSTITUCIONAL" if pred[0] == -1 else "VAREJO"

    def calcular_pressao_espectro(self, p_atual):
        """[SPRINT 3] Mede a fricção e compressão de ordens"""
        if len(self.memoria_ticks) < 10: return 0.0
        volatilidade = np.std(self.memoria_ticks)
        saturacao = 100 - min(volatilidade * 800000, 100)
        return saturacao

    def processar_v15_pro(self, p_atual, ohlc_df):
        # 1. Musculatura (Z-Score)
        precos = ohlc_df['Close'].values.reshape(-1, 1)
        scaler = StandardScaler()
        z_score = float(scaler.fit_transform(precos)[-1][0])
        
        # 2. Inteligência de Padrão (ML)
        status_ml = self.analisar_padrao_ml(p_atual)
        
        # 3. Probabilidade Pura (Monte Carlo)
        vol_est = np.std(self.memoria_ticks) if len(self.memoria_ticks) > 2 else 0.0001
        prob_mc = self.simular_monte_carlo(p_atual, vol_est)
        
        # 4. Saturação (Espectro)
        sat_nivel = self.calcular_pressao_espectro(p_atual)
        
        # 5. Convergência Bayesiana (Fusão de todas as Sprints)
        # Se Z-Score é alto, ML detecta anomalia e MC confirma reversão -> Sinal Forte
        evidencia = prob_mc if (abs(z_score) > 1.5 and status_ml == "INSTITUCIONAL") else 0.45
        self.confianca_bayes = (evidencia * self.confianca_bayes) / \
                               ((evidencia * self.confianca_bayes) + (0.5 * (1 - self.confianca_bayes)))
        
        # 6. Gestão de Risco (Kelly Criterion adaptado)
        k_fator = max(0, ((self.confianca_bayes * 1.8) - 0.8) * 0.03)
        
        return {
            "p_atual": p_atual,
            "confianca": self.confianca_bayes * 100,
            "saturacao": sat_nivel,
            "ml": status_ml,
            "z_score": z_score,
            "lote": round(self.banca_referencia * k_fator, 2),
            "bias": "CALL (ALTA)" if z_score < 0 else "PUT (BAIXA)",
            "alerta": "CONVERGÊNCIA" if (self.confianca_bayes > 0.88) else "ESTÁVEL"
        }

# ==========================================
# 📱 INTERFACE WEB ADAPTADA (Flet)
# ==========================================
def main(page: ft.Page):
    page.title = "AURAXIS SENTINEL V15 PRO"
    page.bgcolor = "#000000"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    
    core = AuraxisCore()
    
    # Elementos de UI
    lbl_price = ft.Text("0.00000", size=50, weight="bold", font_family="monospace")
    lbl_bias = ft.Text("CALIBRANDO SISTEMA...", size=16, color="cyan")
    
    bar_confianca = ft.ProgressBar(value=0.5, color="cyan", bgcolor="#111111", height=15)
    txt_confianca = ft.Text("CONFIANÇA BAYESIANA: 50%", size=14, weight="bold")
    
    bar_saturacao = ft.ProgressBar(value=0.0, color="orange", bgcolor="#111111")
    txt_saturacao = ft.Text("PRESSÃO DO ESPECTRO: 0%", size=12, color="orange")

    chart = ft.LineChart(
        data_series=[ft.LineChartData(color="cyan", stroke_width=2, curved=True,
                                     below_line_bgcolor=ft.colors.with_opacity(0.1, "cyan"))],
        expand=True, min_y=0, max_y=0
    )

    card_ml = ft.Container(content=ft.Column([ft.Text("FLOW ML", size=10), ft.Text("---", size=16, weight="bold")]), 
                          bgcolor="#0a0a0a", padding=15, border_radius=10, expand=True, border=ft.border.all(1, "white10"))
    
    card_lote = ft.Container(content=ft.Column([ft.Text("LOTE SUGERIDO", size=10), ft.Text("0.00", size=16, weight="bold")]), 
                          bgcolor="#0a0a0a", padding=15, border_radius=10, expand=True, border=ft.border.all(1, "white10"))

    page.add(
        ft.Column([
            ft.Row([ft.Text("AURAXIS V15 PRO", weight="bold"), ft.Icon(ft.icons.VERIFIED_USER, color="cyan", size=16)], alignment="spaceBetween"),
            lbl_price,
            lbl_bias,
            ft.Container(chart, height=200, padding=10),
            txt_confianca, bar_confianca,
            ft.Row([card_ml, card_lote]),
            txt_saturacao, bar_saturacao,
            ft.Divider(color="white10"),
            ft.Text("SISTEMA DE AUDITORIA QUANTITATIVA | WEB APP", size=10, color="grey")
        ], expand=True)
    )

    def sensor_pump():
        i = 0
        ohlc_cache = None
        points = []
        while True:
            try:
                if i % 12 == 0: ohlc_cache = yf.download("EURUSD=X", period="1d", interval="1m", progress=False)
                p_atual = yf.Ticker("EURUSD=X").fast_info['last_price'] - core.offset
                
                if ohlc_cache is not None:
                    intel = core.processar_v15_pro(p_atual, ohlc_cache)
                    
                    # Atualização da Interface
                    lbl_price.value = f"{p_atual:.5f}"
                    lbl_price.color = "green" if "CALL" in intel['bias'] else "red"
                    lbl_bias.value = f"SUGESTÃO: {intel['bias']}"
                    lbl_bias.color = lbl_price.color
                    
                    txt_confianca.value = f"CONFIANÇA BAYESIANA: {intel['confianca']:.1f}%"
                    bar_confianca.value = intel['confianca'] / 100
                    
                    txt_saturacao.value = f"PRESSÃO DO ESPECTRO: {intel['saturacao']:.1f}%"
                    bar_saturacao.value = intel['saturacao'] / 100
                    
                    card_ml.content.controls[1].value = intel['ml']
                    card_lote.content.controls[1].value = f"{intel['lote']}"
                    
                    # Gráfico Dinâmico
                    points.append(ft.LineChartDataPoint(i, p_atual))
                    if len(points) > 20: points.pop(0)
                    chart.min_y = min([p.y for p in points]) - 0.0001
                    chart.max_y = max([p.y for p in points]) + 0.0001
                    chart.data_series[0].data_points = points

                page.update()
            except Exception as e: print(f"Erro: {e}")
            i += 1
            time.sleep(5)

    threading.Thread(target=sensor_pump, daemon=True).start()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
