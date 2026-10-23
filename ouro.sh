#!/bin/bash

# Funcao para obter o preco atual da onca troy de ouro em reais
get_gold_ounce_price() {
    # Faz o download da pagina da cotacao do ouro
    html=$(curl -s "https://www.meelion.com/indicadores-financeiros/ouro-hoje/")
    
    # Extrai o valor da onca (valores entre 500-5000 reais)
# Linha corrigida:
price=$(echo "$html" | grep -Eo 'R\$[[:space:]]*[0-9]{3,4},[0-9]+' | head -1 | sed 's/[^0-9,]//g' | sed 's/,/./')    
    echo "$price"
}

# Obtem o valor da onca de ouro
gold_ounce_price=$(get_gold_ounce_price)

if [ -n "$gold_ounce_price" ]; then
    # Calcula margem de lucro de 15%
    lucro=0.15
    valor_com_lucro=$(echo "scale=2; $gold_ounce_price * (1 + $lucro)" | bc -l)
    
    # Formata saida com 2 casas decimais
    ouro_formatado=$(echo "scale=2; $valor_com_lucro / 1" | bc | sed 's/\./,/')
    
    echo "$ouro_formatado"
else
    echo "Nao foi possivel obter a cotacao atual da onca de ouro."
fi
