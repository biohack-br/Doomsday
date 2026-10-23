#!/bin/bash

valor_gasolina=$(./gasolina.sh)
valor_petroleo=$(./petroleo.sh)
valor_dolar=$(./dolar.sh)
valor_moeda=$(./prata.sh)
valor_ouro=$(./ouro.sh)
valor_bitcoin=$(./bitcoin.sh)
tempo_graus=$(./clima.sh)

echo "Indaiatuba: ${tempo_graus}ºC | ${valor_gasolina} | Petroleo: ${valor_petroleo} | ${valor_dolar} | Prata: ${valor_moeda} | Ouro: ${valor_ouro} | Bitoin: ${valor_bitcoin}"
