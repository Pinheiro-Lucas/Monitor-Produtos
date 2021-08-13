import requests
import json
import time
import os
from threading import Timer
from bs4 import BeautifulSoup

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
    json.dump({"jbl": [], "kabum": [], "magalu": []}, arquivo)
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

def preco_alto(qtd_esg, item):
    qtd_esg += 1
    print(f'[{qtd_esg}] PREÇO ALTO: {item}')
    time.sleep(delay)
    return qtd_esg

def estrutura_webhook(produto):
    # Criação da estrutura
    estrutura = {"username": "MONITOR DE PRODUTOS", "content": produto}
    # Já deixei na função caso queira adicionar e organizar a parte Embed
    return estrutura

def checar(produtos, soldout, preco_atual, qtd_esg, qtd_est):
    global webhook, ultimo_produto
    for produto in produtos:

        # Recupera os elementos da página
        try:
            tentativa2 = requests.get(produto[0], allow_redirects=False)

            # Se tiver estoque
            if tentativa2.text.lower().count(soldout) == 0:

                # Utilização de raspagem de dados (nesse caso: o preço)
                soup = BeautifulSoup(tentativa2.text, features="html.parser")
                preco = soup.find_all(preco_atual[0], {preco_atual[1]: preco_atual[2][0]})

                # Tenta a segunda opção de procura pelo preço (lojas com diferentes displays de produtos)
                if not preco:
                    preco = soup.find_all(preco_atual[0], {preco_atual[1]: preco_atual[2][1]})

                # Filtrando os dados
                preco_real = ''
                for i in list(str(preco)):
                    if i in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
                        preco_real += i

                # Encontrado o preço (em int e sem ,00)
                preco = preco_real[0:len(preco_real) - 2]

                # Depois de rodar algumas milhares de vezes, o site pode falhar em retornar e isso previne crashs
                if preco == '':
                    preco = None
                else:
                    preco = int(preco)

                # Se o preço do produto em estoque for menor ou igual ao esperado
                if preco is not None and preco <= produto[1]:
                    # Fix para não ficar apitando o mesmo produto milhares de vezes
                    if not produto[0] == ultimo_produto:
                        requests.post(webhook, json=estrutura_webhook(produto[0]))
                    ultimo_produto = produto[0]
                    # Log dos produtos em estoque com o preço bom
                    qtd_est = em_estoque(qtd_est, produto[0])
                # Se o preço não estiver bom
                else:
                    # Log de preço alto
                    qtd_esg = preco_alto(qtd_esg, produto[0])
                    # Se o último produto com estoque estiver sem estoque, ele reseta para não bugar
                    if produto[0] == ultimo_produto:
                        ultimo_produto = ''
            # Esgotado
            else:
                # Log de esgotado
                qtd_esg = esgotado(qtd_esg, produto[0])
                # Se o último produto com estoque estiver sem estoque, ele reseta para não bugar
                if produto[0] == ultimo_produto:
                    ultimo_produto = ''

        # Caso o Link esteja errado ele avisará
        except:
            requests.post(webhook, json=estrutura_webhook(f'**OCORREU UM ERRO AO MONITORAR O PRODUTO:** {produto[0]}'))

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
                preco_atual = ['span', 'class', ['boleto-price']]
                produtos = lista.get("jbl")
                qtd_esg, qtd_est = checar(produtos, soldout, preco_atual, qtd_esg, qtd_est)
            elif item == 'kabum':
                soldout = 'produto_indisponivel'
                preco_atual = ['span', 'class', ['preco_desconto_avista-cm', 'preco_desconto']]
                produtos = lista.get("kabum")
                qtd_esg, qtd_est = checar(produtos, soldout, preco_atual, qtd_esg, qtd_est)
            elif item == 'magalu':
                soldout = 'unavailable__product-title'
                preco_atual = ['span', 'class', ['price-template__text']]
                produtos = lista.get("magalu")
                qtd_esg, qtd_est = checar(produtos, soldout, preco_atual, qtd_esg, qtd_est)

# Função para adicionar Links/Lojas
def adicionar_url():
    # Coleta as informações
    loja, nova_url, preco = '', '', -1

    while loja not in ('jbl', 'kabum', 'magalu'):
        loja = input('Insira o nome da loja (jbl, kabum, magalu): ').lower()

    while nova_url.count('http') == 0:
        nova_url = input('Insira a URL do produto: ')

    while preco == -1:
        preco = int(input('Insira o preço máximo sem vírgula ou ponto (0 = sem max.): '))

    # Carrega o arquivo
    info = json.load(open('links.json', 'r'))

    # Checa se a URL já foi cadastrada
    if loja in info.keys() and nova_url in info.get(loja):
        print('\n[AVISO] URL já cadastrada!')
    else:
        # Checa se a loja já contém alguma URL
        if loja in info.keys():
            info_antiga = info.get(loja)
            info_antiga.append([nova_url, preco])
            info.update({loja: info_antiga})
        else:
            info.update({loja: [nova_url, preco]})
        # Salva o arquivo
        json.dump(info, open('links.json', 'w'))


erros = 0
def iniciar():
    global erros
    try:
        checar_estoque(json.load(open('links.json', 'r')))
    finally:
        erros += 1
        if not erros > 5:
            requests.post(webhook, json=estrutura_webhook('__**OCORREU UM ERRO AO INICIAR O MONITORAMENTO**__'))
            iniciar()
        else:
            print('[AVISO] Máximo de tentativas atingido')
            exit()


# Timer caso não haja escolha ele comece a monitorar
timer = Timer(10, iniciar)
timer.start()

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
        timer.cancel()
        adicionar_url()
    elif escolha == '2':
        # Inicia o monitoramento
        timer.cancel()
        flag = True
        iniciar()
