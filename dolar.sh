#!/bin/bash

# URL da API que retorna o JSON com a cotação do dólar
url="https://economia.awesomeapi.com.br/json/last/USD-BRL"

# Baixa o conteúdo da API e extrai a cotação do dólar usando jq
dolar=$(curl -s "$url" | jq -r '.USDBRL.ask')

# Exibir a cotação formatada
if [ -n "$dolar" ]; then
    # Converter para formato numérico com duas casas decimais
    dolar_formatado=$(LC_NUMERIC="en_US.UTF-8" printf "%.2f" "$dolar")
    
    # Substituir ponto por vírgula para o formato R$ 5,44
    dolar_formatado=$(echo "$dolar_formatado" | sed 's/\./,/')
    
    # Exibir o resultado formatado
    echo "Dólar: R$ $dolar_formatado"
else
    echo "Não foi possível obter a cotação do dólar."
fi
