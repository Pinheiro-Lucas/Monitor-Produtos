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
    json.dump({}, arquivo)
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

# Função para adicionar Links/Lojas
def adicionar_url():
    # Coleta as informações
    loja = ''
    while loja.lower() not in ('jbl', 'nike'):
        loja = input('Insira o nome da loja (jbl ou nike): ')
    nova_url = input('Insira a URL do produto: ')
    
    # Salva no arquivo
    info = json.load(open('links.json', 'r'))
    if loja in info.keys():
        info_antiga = info.get(loja)
        info_antiga.append(nova_url)
        info.update({loja: info_antiga})
    else:
        info.update({loja: nova_url})
    json.dump(info, open('links.json', 'w'))
    menu_escolhas()


# Ao abrir, escolher uma das opções
def menu_escolhas():
    escolha = ''
    while escolha not in ('1', '2'):
        escolha = input("""
                            ESCOLHA UMA OPÇÃO:
                            [1] Adicionar URL
                            [2] Checar Estoques
    
                        """)

    if escolha == '1':
        # Preciso fazer ainda
        adicionar_url()
    elif escolha == '2':
        # Inicia o monitoramento
        checar_estoque(json.load(open('links.json', 'r')))


menu_escolhas()
