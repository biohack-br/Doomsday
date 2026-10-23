#!/bin/bash
#
# update.sh — coleta clima + cotações e grava quotes_cache.json
#

set -u

# --- Diretório base (funciona de qualquer CWD) ---
DIR="$(cd "$(dirname "$0")" && pwd)"
QUOTES_FILE="$DIR/quotes_cache.json"
LOG_FILE="$DIR/quotes_cron.log"

# --- Helper: roda script e devolve saída ou default ---
run_script() {
    local script=$1
    local default=$2
    local result

    if [ -f "$script" ]; then
        result=$(bash "$script" 2>/dev/null)
        if [ -n "$result" ] && [ "$result" != "N/A" ] && [ "$result" != "0" ]; then
            printf '%s' "$result"
        else
            printf '%s' "$default"
        fi
    else
        printf '%s' "$default"
    fi
}

# --- 1) Clima ---
TEMP_OUT=$(run_script "$DIR/clima.sh" "")

TEMPERATURA="N/A"
TEMP_NUM=""

if [[ "$TEMP_OUT" =~ ^-?[0-9]+([.][0-9]+)?$ ]]; then
    TEMP_NUM="$TEMP_OUT"
elif [ -f "$DIR/clima.json" ]; then
    t=$(jq -r '.current_condition[0].temp_C // empty' "$DIR/clima.json" 2>/dev/null)
    if [ -n "$t" ] && [ "$t" != "null" ]; then
        TEMP_NUM="$t"
    fi
fi

# Formata com ºC (só se conseguiu número)
if [ -n "$TEMP_NUM" ]; then
    TEMPERATURA="${TEMP_NUM}ºC"
fi

# --- 2) Cotações ---
GASOLINA=$(run_script "$DIR/gasolina.sh" "Gasolina SP: N/A")
PETROLEO=$(run_script "$DIR/petroleo.sh" "Petroleo: N/A")
DOLAR=$(run_script   "$DIR/dolar.sh"    "Dolar: N/A")
PRATA=$(run_script   "$DIR/prata.sh"    "Prata: N/A")
OURO=$(run_script    "$DIR/ouro.sh"     "Ouro: N/A")
BITCOIN=$(run_script "$DIR/bitcoin.sh"  "BitCoin: N/A")

# --- 3) JSON (jq -n: seguro contra aspas, barras, $ e newlines) ---
jq -n \
  --arg last_update "$(date '+%d/%m/%Y %H:%M:%S')" \
  --arg temperatura  "$TEMPERATURA" \
  --arg gasolina     "$GASOLINA" \
  --arg petroleo     "$PETROLEO" \
  --arg dolar        "$DOLAR" \
  --arg prata        "$PRATA" \
  --arg ouro         "$OURO" \
  --arg bitcoin      "$BITCOIN" \
  '{
     last_update: $last_update,
     temperatura: $temperatura,
     gasolina:    $gasolina,
     petroleo:    $petroleo,
     dolar:       $dolar,
     prata:       $prata,
     ouro:        $ouro,
     bitcoin:     $bitcoin
   }' > "$QUOTES_FILE"

# --- 4) Permissões (descomente se usar com www-data) ---
# chmod 666 "$QUOTES_FILE"
# chown www-data:www-data "$QUOTES_FILE"

# --- 5) Log ---
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Cotação atualizada (temp=$TEMPERATURA)" >> "$LOG_FILE"
