#!/bin/bash

# Baixa o conteúdo da página e extrai o valor do campo <p id="telafinal-precofinal">
preco=$(python3 ./gasolina.py)

# Exibe o resultado
if [ -n "$preco" ]; then
    echo "Gasolina SP: $preco"
else
    echo "/NA"
fi
