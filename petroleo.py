#!/usr/bin/env python3
"""
Consulta a cotação mais recente disponível dos futuros de petróleo Brent (BZ=F)
pela API de gráfico do Yahoo Finance.

Requisito:
    python3 -m pip install requests

Uso:
    python3 petroleo.py
"""
import sys
import math
import requests

URL = "https://query1.finance.yahoo.com/v8/finance/chart/BZ%3DF"
PARAMS = {"range": "5d", "interval": "1d"}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
}

def main():
    try:
        response = requests.get(
            URL, params=PARAMS, headers=HEADERS, timeout=20
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "desconhecido"
        print(f"ERRO: a fonte de cotação respondeu HTTP {status}.", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as exc:
        print(f"ERRO: falha de conexão ao consultar a cotação: {exc}", file=sys.stderr)
        return 1

    try:
        data = response.json()
        chart = data.get("chart", {})
        if chart.get("error"):
            raise ValueError(str(chart["error"]))
        result = chart["result"][0]
        price = result.get("meta", {}).get("regularMarketPrice")

        if price is None:
            closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
            price = next((value for value in reversed(closes) if value is not None), None)

        if price is None or not math.isfinite(float(price)) or float(price) <= 0:
            raise ValueError("preço ausente ou inválido")

        print(f"USD {float(price):.2f}")
        return 0
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        print(f"ERRO: não foi possível interpretar uma cotação válida: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
