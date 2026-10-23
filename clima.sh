#!/bin/bash

CIDADE="Indaiatuba"
JSONFILE="clima.json"

cleanup() {
    rm -f "$JSONFILE"
}

# Executa e garante limpeza ao sair
trap cleanup EXIT

curl -s "https://wttr.in/${CIDADE}?format=j1" -o "$JSONFILE"

if [ ! -s "$JSONFILE" ]; then
    echo "N/A"
    exit 1
fi

tempo_graus=$(jq -r '.current_condition[0].temp_C // empty' "$JSONFILE")

if [ -z "$tempo_graus" ] || [ "$tempo_graus" = "null" ]; then
    echo "N/A"
    exit 1
fi

# Só imprime o número — o info.sh formata
echo "$tempo_graus"
