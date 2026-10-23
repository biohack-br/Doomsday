#!/bin/bash

# Função para obter o preço atual da prata por onça troy em dólares usando a API do CoinGecko
get_silver_price() {
    # Usando curl para fazer uma requisição GET para a API do CoinGecko
    response=$(curl -s "https://api.coingecko.com/api/v3/simple/price?ids=silver-spot&vs_currencies=brl")
    # Extrair o preço da prata em dólares da resposta JSON
    silver_price_brl=$(echo "$response" | jq -r '.["silver-spot"].brl')

    echo "$silver_price_brl"
}

# Obtendo o preço atual da prata por onça troy em dólares
silver_price_brl=$(get_silver_price)

if [ -n "$silver_price_brl" ]; then

    # Calculando o valor de uma moeda de prata (assumindo uma onça troy)
    valor_moeda=$(echo "scale=2; $silver_price_brl * 3.11035" | bc -l)

    # Calculando a margem de lucro de 15%
    lucro=0.15
    valor_com_lucro=$(echo "scale=2; $valor_moeda * (1 + $lucro)" | bc -l)

    prata_formatado=$(LC_NUMERIC="en_US.UTF-8" printf "%.2f" "$valor_com_lucro")

    # Exibindo o valor da moeda de prata em reais
    echo "R$ $prata_formatado"
else
    echo "Não foi possível obter a cotação atual da prata. Verifique sua conexão com a internet ou tente novamente mais tarde."
fi
