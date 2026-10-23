#!/data/data/com.termux/files/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re

url = "http://precos.petrobras.com.br/w/gasolina/sp"

try:
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Procura pelo elemento
    elemento = soup.find('p', {'id': 'telafinal-precofinal'})
    
    if elemento:
        preco = elemento.text.strip()
        print(f"R$ {preco}")
    else:
        # Tenta buscar por expressão regular
        padrao = r'id="telafinal-precofinal"[^>]*>([0-9,]+)'
        match = re.search(padrao, response.text)
        if match:
            print(f"R$ {match.group(1)}")
        else:
            print("Não foi possível obter o preço.")
            
except Exception as e:
    print(f"Erro: {e}")
