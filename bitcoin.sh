#!/bin/bash

# Bitcoin em Dólar - Arredondar para inteiro (sem centavos)
url_bitcoin="https://economia.awesomeapi.com.br/json/last/BTC-USD"
bitcoin_data=$(curl -s "$url_bitcoin")
bitcoin=$(echo "$bitcoin_data" | jq -r '.BTCUSD.ask // "null"' 2>/dev/null || echo "null")

if [ "$bitcoin" != "null" ] && [ -n "$bitcoin" ]; then
    # Arredondar para inteiro (remover decimais)
    bitcoin_inteiro=$(echo "$bitcoin" | awk '{printf "%.0f", $1}')
    # Formatar com pontos para milhares
    bitcoin_formatado=$(echo "$bitcoin_inteiro" | awk '{len=length($0); for(i=len-2; i>1; i-=3) $0=substr($0,1,i-1) "." substr($0,i); print $0}')
   echo "$""USD $bitcoin_formatado"
else
    bitcoin_formatado="null"
fi
