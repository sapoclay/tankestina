import random
from graficos import ANCHO, ALTO, TAM_TANQUE

def nueva_posicion_enemigo():
    x_enemigo = random.randint(ANCHO//2 + 50, ANCHO - TAM_TANQUE - 20)
    y_enemigo = ALTO - 50
    return x_enemigo, y_enemigo

def nueva_posicion_muro():
    muro_x = random.randint(ANCHO//3, 2*ANCHO//3)
    muro_altura = random.randint(100, 300)
    return muro_x, muro_altura
