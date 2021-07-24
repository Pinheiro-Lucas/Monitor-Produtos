import requests
import json
import time
import os

# Importando configurações
config = json.load(open('config.json', 'r'))
webhook = config['webhook']
delay = config['delay']

# Se não tiver o arquivo 'links.json', ele cria um vazio
if not os.path.isfile('links.json'):
    print('[LOG] Criando arquivo de Links..')
    arquivo = open('links.json', 'w')
    json.dump([], arquivo)
    arquivo.close()
    print('[LOG] Arquivo dos Links criado com sucesso.')

# Adiantando uma função que será necessária futuramente
def esgotado(qtd_esg, item):
    qtd_esg += 1
    print(f'[{qtd_esg}] ESGOTADO: {item}')
    time.sleep(delay)

# Adiantando uma função que será necessária futuramente
def em_estoque(qtd_est, item):
    qtd_est += 1
    print(f'[{qtd_est}] EM ESTOQUE: {item}')
    time.sleep(delay)

# Função de checagem de estoque
def checar_estoque(lista):
    print('[LOG] Checando estoques:')
    global delay
    qtd_esg, qtd_est = 0, 0

    # Fica checando o estoque de cada produto
    while True:
        for item in lista:
            tentativa2 = requests.get(item)
            # Falta função de detecção de cada site
            if tentativa2.text.lower().count('not-available') > 0:
                esgotado(qtd_esg, item)
            else:
                em_estoque(qtd_est, item)


# Ao abrir, escolher uma das opções
escolha = ''
while escolha not in ('1', '2'):
    escolha = input("""
                        ESCOLHA UMA OPÇÃO:
                        [1] Checar URLs
                        [2] Checar Estoques

                    """)

if escolha == '1':
    # Preciso fazer ainda
    print()
elif escolha == '2':
    # Inicia o monitoramento
    checar_estoque(json.load(open('links.json', 'r')))
