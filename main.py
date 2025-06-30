#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 30 10:46:03 2025

@author: tercio
"""

import cv2
import math
import pandas as pd
from variaveis import tamanho_quadrado_real, suj,bloco, n_tt, media, desvio_padrao, fator_do_dp, cam, altura_da_tela,largura_da_tela

# Lista para armazenar os pontos clicados
pontos = []
distancia_pixels = None  # Definido fora da função
distancia_cruz_centimetros = None 
matriz_homografia = None

dp = desvio_padrao
erros = []
p_bola_x = []
p_bola_y = []
p_alvo_x = []
p_alvo_y = [] 
r = []

# Função que será chamada ao clicar com o mouse
def clique(event, x, y, flags, param):
    
    global distancia_pixels 
    global distancia_cruz_centimetros
    global tentativa
    global tentativas
    if event == cv2.EVENT_LBUTTONDOWN:
        
        pontos.append((x, y))
        
        # Se já tiver clicado em 4 pontos, calcular a conversão
        if len(pontos) >= 4:
            if len (pontos) ==4:              

                # Calcular as distâncias entre os pontos (usando apenas dois pontos opostos)
                distancia_pixels = math.sqrt((pontos[0][0] - pontos[2][0]) ** 2 + (pontos[0][1] - pontos[2][1]) ** 2)
                
            else:

                # Calcular o fator de conversão (pixels por metro)
                fator_conversao = distancia_pixels / tamanho_quadrado_real
               
            
                # Agora, vamos calcular a distância até a cruz (ponto clicado e centro da tela)
                distancia_cruz_pixels = math.sqrt((x - centro_x) ** 2 + (y - centro_y) ** 2)
                

                # Converter a distância de pixels para metros
                distancia_cruz_metros = distancia_cruz_pixels / fator_conversao
                
            
                # Se quiser também em centímetros
                distancia_cruz_centimetros = distancia_cruz_metros * 100
                
                erros.append(distancia_cruz_centimetros)
                
                p_alvo_x.append(centro_x)
                p_alvo_y.append(centro_y)
                p_bola_x.append(x)
                p_bola_y.append(y)
                if distancia_cruz_centimetros > media - (dp * fator_do_dp):
                    r.append("busque")
                else:
                    r.append("nao_busque")
                

# Abrir a câmera (0 = câmera padrão)
camera = cv2.VideoCapture(cam)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, largura_da_tela)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, altura_da_tela)
# Verificar se a câmera foi aberta corretamente
if not camera.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

# Nome da janela
nome_janela = "Tarefa motora"

# Associar a função de clique à janela
cv2.namedWindow(nome_janela)
cv2.setMouseCallback(nome_janela, clique)

print("Clique nos 4 cantos do quadrado.")

# Loop principal
while True:
    ret, frame = camera.read()
    if not ret:
        print("Erro ao capturar imagem da câmera.")
        break

    # Obter as dimensões da imagem (altura, largura)
    altura, largura, _ = frame.shape

    # Definir o centro da tela (onde a cruz será desenhada)
    centro_x, centro_y = largura // 2, altura // 2

    # Desenhar a cruz no centro da tela
    cv2.line(frame, (centro_x - 20, centro_y), (centro_x + 20, centro_y), (75, 0, 130), 2)
    cv2.line(frame, (centro_x, centro_y - 20), (centro_x, centro_y + 20), (75, 0, 130), 2)

    # Exibir os pontos clicados como círculos verdes
    for ponto in pontos:
        cv2.circle(frame, ponto, 5, (0, 0, 255), -1)
        if len(pontos) >4:
            cv2.putText(frame, f"erro: {distancia_cruz_centimetros:.2f}cm", (50, 50),               # Posição (x, y)
                        cv2.FONT_HERSHEY_SIMPLEX,           # Fonte
                        1,                                  # Tamanho do texto
                        (75, 0, 130),                        # Cor (B, G, R) -> vermelho
                        2,                                  # Espessura da linha
                        cv2.LINE_AA)
        if len (erros)> 0:            
            if erros[-1] > media-(dp*fator_do_dp): #coloquei menos para ficar mais exigente
                resposta = "busque a bola"          
              
            else:
                resposta = "Nao busque"
                
                
            
            
                
            cv2.putText(frame, resposta, (800, 50),               # Posição (x, y)
                        cv2.FONT_HERSHEY_SIMPLEX,           # Fonte
                        1,                                  # Tamanho do texto
                        (75, 0, 130),                        # Cor (B, G, R) -> vermelho
                        2,                                  # Espessura da linha
                        cv2.LINE_AA)
            
            

    # Exibir a imagem
    cv2.imshow(nome_janela, frame)

    # Sai do loop se a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == 27:
        break
    if n_tt == len(erros):
        break
    

# Libera a câmera e fecha as janelas
camera.release()
cv2.destroyAllWindows()
# Salva o frame como imagem
cv2.imwrite("resultados/suj_"+str(suj)+"_bloco_"+str(bloco)+".png", frame)

df= pd.DataFrame({
    'erro_radial_cm': erros,
    'p_bola_x_px': p_bola_x,
    'p_bola_y_px': p_bola_y,
    'p_alvo_x_px': p_alvo_x,
    'p_alvo_y_px': p_alvo_y,
    "bucar": r
    
})
df.to_excel("resultados/suj_"+str(suj)+"_bloco_"+str(bloco)+".xlsx", index=False)


