import requests
import json
import time
import os

# Importando configurações
config = json.load(open('config.json', 'r'))
webhook = config['webhook']
delay = config['delay']
ultimo_produto = ''

if webhook.count('http') == 0:
    print('[ERRO] Insira um Webhook válido')
    exit()

# Se não tiver o arquivo 'links.json', ele cria um vazio
if not os.path.isfile('links.json'):
    print('[LOG] Criando arquivo de Links..')
    arquivo = open('links.json', 'w')
    json.dump({"jbl": [], "kabum": []}, arquivo)
    arquivo.close()
    print('[LOG] Arquivo dos Links criado com sucesso.')

# Adiantando uma função que será necessária futuramente
def esgotado(qtd_esg, item):
    qtd_esg += 1
    print(f'[{qtd_esg}] ESGOTADO: {item}')
    time.sleep(delay)
    return qtd_esg

# Adiantando uma função que será necessária futuramente
def em_estoque(qtd_est, item):
    qtd_est += 1
    print(f'[{qtd_est}] EM ESTOQUE: {item}')
    time.sleep(delay)
    return qtd_est

def estrutura_webhook(produto):
    # Criação da estrutura + embed
    estrutura = {"username": "BOT RESTOCK", "content": produto}
    return estrutura

def checar(produtos, soldout, qtd_esg, qtd_est):
    global webhook, ultimo_produto
    for produto in produtos:
        # Checagem do estoque
        tentativa2 = requests.get(produto)
        if tentativa2.text.lower().count(soldout) > 0:
            qtd_esg = esgotado(qtd_esg, produto)
        else:
            if not produto == ultimo_produto:
                requests.post(webhook, json=estrutura_webhook(produto))
            ultimo_produto = produto
            qtd_est = em_estoque(qtd_est, produto)
    return qtd_esg, qtd_est

# Função de checagem de estoque
def checar_estoque(lista):
    print('[LOG] Checando estoques:')
    global delay
    qtd_esg, qtd_est = 0, 0

    # Fica checando o estoque de cada produto
    while True:
        # Cada loja existe uma técnica de checagem
        for item in lista.keys():
            # Lista os produtos cadastrados
            if item == 'jbl':
                soldout = 'not-available'
                produtos = lista.get("jbl")
                qtd_esg, qtd_est = checar(produtos, soldout, qtd_esg, qtd_est)
            elif item == 'kabum':
                soldout = 'produto_indisponivel'
                produtos = lista.get("kabum")
                qtd_esg, qtd_est = checar(produtos, soldout, qtd_esg, qtd_est)

# Função para adicionar Links/Lojas
def adicionar_url():
    # Coleta as informações
    loja = ''
    while loja.lower() not in ('jbl', 'kabum'):
        loja = input('Insira o nome da loja (jbl ou kabum): ')
    nova_url = input('Insira a URL do produto: ')
    
    # Carrega o arquivo
    info = json.load(open('links.json', 'r'))

    # Checa se a URL já foi cadastrada
    if loja in info.keys() and nova_url in info.get(loja):
        print('\n[AVISO] URL já cadastrada!')
    elif nova_url.count('http') == 0:
        print('\n[AVISO] Insira uma URL válida!')
    else:
        # Checa se a loja já contém alguma URL
        if loja in info.keys():
            info_antiga = info.get(loja)
            info_antiga.append(nova_url)
            info.update({loja: info_antiga})
        else:
            info.update({loja: nova_url})
        # Salva o arquivo
        json.dump(info, open('links.json', 'w'))


# Ao abrir, escolher uma das opções
escolha = ''
flag = False
while escolha not in ('1', '2') or not flag:
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
        flag = True
        checar_estoque(json.load(open('links.json', 'r')))
