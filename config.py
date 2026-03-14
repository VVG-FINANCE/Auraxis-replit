# =========================
# config.py - Auraxis robusto
# =========================

# =========================
# Chaves de API públicas
# =========================
API_KEYS = {
    "exchangerate_api": "SUA_CHAVE_AQUI",
    "frankfurter_api": "SUA_CHAVE_AQUI",
    "yfinance": None  # yfinance não precisa de chave
}

# =========================
# Parâmetros de trading
# =========================
TRADING_CONFIG = {
    "pares": ["EUR/USD"],           # Apenas EUR/USD
    "tipos_trader": ["scalper", "day", "swing", "position"],
    "entrada_dupla": True,          # Habilita entrada externa + interna
    "limites_zona": {               # Zonas para entradas, stop e take
        "entrada": {"superior": 0.0003, "inferior": 0.0001},
        "stop": {"superior": 0.0012, "inferior": 0.0008},
        "take": {"superior": 0.0025, "inferior": 0.0015}
    },
    "rr_min": 1.5,                  # RR mínimo aceito
    "score_default": 80,            # Score inicial padrão
    "fragmentacao_segundos": 5,     # Atualização de candles em segundos
    "ajuste_max_pips": 30           # Ajuste máximo em pips (positivo ou negativo)
}

# =========================
# Fallback e limites
# =========================
FALLBACK_CONFIG = {
    "usar_yfinance": True,               # Ativa fallback se APIs falharem
    "ultimo_candle_padrao": 1.16100,    # fallback interno se todas falharem
    "tempo_max_retry_segundos": 60       # máximo de tempo para tentativa de API
}

# =========================
# Configurações de interface (mobile)
# =========================
UI_CONFIG = {
    "cores": {
        "background": "#121212",
        "texto": "#FFFFFF",
        "positivo": "#00FF00",
        "negativo": "#FF0000",
        "entrada": "#1E90FF",
        "take": "#FFD700",
        "stop": "#FF4500"
    },
    "font_size": {
        "principal": 20,
        "secundario": 16
    },
    "abas": ["Mercado", "Oportunidades", "Histórico"]
}
