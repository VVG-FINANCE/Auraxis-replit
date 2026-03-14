from flask import Flask, render_template, jsonify, request
from engine.core import EngineCore
from threading import Thread
import time

app = Flask(__name__)
engine = EngineCore()
engine.iniciar_loop()  # Inicia o loop do motor central

# =========================
# Página principal
# =========================
@app.route('/')
def index():
    return render_template("index.html")

# =========================
# API: preço atual
# =========================
@app.route('/api/preco')
def preco():
    ultimo_candle = engine.historico_candles[-1] if engine.historico_candles else {}
    preco = ultimo_candle.get("close", 0.0)
    delta = round(preco - ultimo_candle.get("open", preco), 5) if ultimo_candle else 0.0
    return jsonify({
        "preco": round(preco,5),
        "delta": delta
    })

# =========================
# API: oportunidades por tipo de trader
# =========================
@app.route('/api/oportunidades/<trader_type>')
def oportunidades(trader_type):
    opps = engine.obter_oportunidades(trader_type)
    return jsonify(opps)

# =========================
# API: ajustar pips manualmente
# =========================
@app.route('/api/ajustar_pips', methods=["POST"])
def ajustar_pips():
    data = request.json
    pips = float(data.get("pips", 0))
    engine.ajustar_preco_manual(pips)
    return jsonify({"status":"ok", "pips_ajustados":pips})

# =========================
# API: simulação Monte Carlo
# =========================
@app.route('/api/simulacao')
def simulacao():
    nivel = float(request.args.get("nivel", 0))
    prob = engine.probabilidade_alcance(nivel)
    return jsonify({"nivel":nivel, "probabilidade":prob})

# =========================
# Inicializa servidor
# =========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
