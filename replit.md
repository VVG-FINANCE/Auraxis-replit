# AURAXIS SENTINEL V15 PRO

## Overview
A quantitative trading analysis dashboard built with Python and Flet (Flutter-based UI framework). It tracks EUR/USD forex prices in real-time using Yahoo Finance, applying machine learning and statistical analysis to generate trading signals.

## Architecture
- **Language**: Python 3.12
- **UI Framework**: Flet 0.82.0 (web mode via flet-web)
- **Data Source**: Yahoo Finance (yfinance) - EUR/USD real-time data
- **ML**: scikit-learn IsolationForest for anomaly detection
- **Statistics**: NumPy/Pandas for Monte Carlo simulation, Z-Score, Bayesian confidence

## Core Components
- `main.py` - Single-file app containing both the analysis engine and UI
  - `AuraxisCore` class: Quantitative analysis engine (Monte Carlo, ML, Bayesian convergence)
  - `main()` function: Flet UI with real-time price display, confidence bars, and sparkline chart

## Running
- **Workflow**: "Start application" runs `python main.py`
- **Port**: 5000 (web browser view)
- **Host**: 0.0.0.0

## Dependencies
- flet==0.82.0
- flet-web==0.82.0
- yfinance
- pandas
- scikit-learn
- numpy

## Notes
- `ft.LineChart` is not available in flet 0.82.0; replaced with a custom bar-based sparkline using `ft.Container` rows
- Uses `ft.run()` instead of deprecated `ft.app()`
- Fixed `AttributeError: module 'flet.controls.alignment' has no attribute 'center'` by using `ft.Alignment(0, 0)`
- Fixed `AttributeError: module 'flet' has no attribute 'icons.VERIFIED_USER'` by temporarily removing the icon (Flet 0.82.0 icons naming varies)
- Price data fetches every 5 seconds, OHLC data refreshes every 60 seconds
